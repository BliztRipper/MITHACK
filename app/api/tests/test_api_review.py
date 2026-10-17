"""5.5: review queue, confirm/override, amend, Provenance, report status (specs: clinician-review,
fhir-clinical-records)."""
import json
from datetime import datetime, timedelta, timezone

import pytest

import deps
from conftest import login
from rules.text import templates
from test_api_cases import CONSENT, SCREENING, fake_seg, post
from vision import segment

pytestmark = pytest.mark.fhir


@pytest.fixture
def world(live, fhir, patient, monkeypatch):
    monkeypatch.setattr(segment, "segment", fake_seg)
    monkeypatch.setattr(deps, "model", lambda: None)
    login(live, "gp1")
    live.post(f"/patients/{patient}/consent", json=CONSENT)

    def case(mode="emergency"):
        r = post(live, pid=patient) if mode == "emergency" else post(live, "screening", json.dumps(SCREENING), pid=patient)
        return r.json()["report_id"]
    live.case = case
    return live


def test_new_result_is_preliminary_with_ai_label(world):
    c = world.get(f"/cases/{world.case()}").json()
    assert c["status"] == "preliminary" and c["label"] == "AI-assisted, not a diagnosis" and c["can_sign"]


def test_override_recorded_with_reason_identity_time_and_provenance(world, fhir):
    rid = world.case()
    login(world, "oph1")
    r = world.post(f"/cases/{rid}/sign", json={"decision": "override", "finding": "not CRAO",
                                                "reason": "clinical findings disagree", "crao": False})
    assert r.status_code == 200, r.text
    rep = fhir.read("DiagnosticReport", rid)
    assert rep["status"] == "final" and rep["conclusion"] == "not CRAO"  # clinician finding is authoritative
    [rv] = world.get(f"/cases/{rid}").json()["reviews"]
    assert rv["decision"] == "override" and rv["reason"] == "clinical findings disagree" and rv["finding"] == "not CRAO"
    assert rv["user"] == "oph1" and rv["by"].startswith("Practitioner/") and rv["at"]
    assert rv["ai_conclusion"].startswith("ESCALATE")  # the AI output is kept
    provs = {p["agent"][0]["type"]["coding"][0]["code"]: p for p in fhir.search("Provenance", target=f"DiagnosticReport/{rid}")}
    assert provs.keys() == {"assembler", "author"}  # AI device at creation, clinician at signing
    assert provs["author"]["agent"][0]["who"]["reference"] == rv["by"]
    q = [o for o in fhir.search("Observation", subject=rep["subject"]["reference"])
         if o["code"]["coding"][0]["code"] == "image-quality-score"]
    assert q and all(o["device"]["reference"].startswith("Device/") for o in q)  # AI output keeps its Device


def test_override_without_reason_is_blocked(world, fhir):
    rid = world.case()
    r = world.post(f"/cases/{rid}/sign", json={"decision": "override", "finding": "not CRAO", "crao": False})
    assert r.status_code == 422 and "reason" in r.json()["detail"]
    assert fhir.read("DiagnosticReport", rid)["status"] == "preliminary"


def test_emergency_sign_needs_the_clinical_crao_answer(world):
    assert world.post(f"/cases/{world.case()}/sign", json={"decision": "confirm"}).status_code == 422


def test_final_report_has_every_section(world):
    rid = world.case()
    world.post(f"/cases/{rid}/sign", json={"decision": "confirm", "crao": False})
    c = world.get(f"/cases/{rid}").json()
    assert c["status"] == "final" and c["label"] == "AI-assisted, not a diagnosis"
    assert c["patient"]["name"] and c["patient"]["hn"] and c["mode"] == "emergency"
    a = c["analysis"]
    assert a["quality"]["score"] and a["crao"]["status"] == "no model loaded" and a["triage"]["level"] == "ESCALATE"
    assert {m["kind"] for m in c["media"]} == {"fundus", "vessel", "artery_vein", "disc"}
    assert c["reviews"][0]["decision"] == "confirm" and not c["can_sign"]


def test_thai_patient_summary_for_signed_screening_case(world):
    rid = world.case("screening")
    assert world.get(f"/cases/{rid}/summary", params={"lang": "th"}).status_code == 409  # not signed yet
    world.post(f"/cases/{rid}/sign", json={"decision": "confirm"})
    band = world.get(f"/cases/{rid}").json()["analysis"]["risk"]["pce"]["band"]
    th = templates("th")
    assert world.get(f"/cases/{rid}/summary", params={"lang": "th"}).json() == {
        "lang": "th", "text": [th[f"summary.screening.pce.{band}"], th["summary.seek_care"]]}


def test_queue_lists_emergency_first(world, fhir):
    old = world.case("screening")
    rep = fhir.read("DiagnosticReport", old)
    rep["issued"] = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(timespec="seconds")
    fhir.update(rep)
    new = world.case("emergency")
    q = world.get("/review/queue").json()
    ids = [i["report_id"] for i in q]
    assert ids.index(new) < ids.index(old)
    assert q[ids.index(new)]["patient"] == {"name": "Somsri Testapi", "hn": f"TEST-API-{'test_queue_lists_emergency_first'[:20]}"}


def test_layers_shown_at_signing_are_stored_and_returned(world):
    rid = world.case()
    bad = {"decision": "confirm", "crao": False, "layers": {"visible": ["vessel", "x-ray"], "opacity": 70}}
    assert world.post(f"/cases/{rid}/sign", json=bad).status_code == 422
    assert world.post(f"/cases/{rid}/sign", json={**bad, "layers": {"visible": ["disc"], "opacity": 101}}).status_code == 422
    layers = {"visible": ["artery_vein", "disc"], "opacity": 55}
    assert world.post(f"/cases/{rid}/sign", json={**bad, "layers": layers}).status_code == 200
    [rv] = world.get(f"/cases/{rid}").json()["reviews"]
    assert rv["layers"] == layers


def test_escalated_case_reaches_reviewer_with_image_overlays_and_answers(world):
    esc, scr = world.case("emergency"), world.case("screening")
    login(world, "oph1")
    q = {i["report_id"]: i for i in world.get("/review/queue").json()}
    assert esc in q and scr not in q
    assert q[esc]["level"] == "ESCALATE" and q[esc]["inputs"]["hours_since_onset"] == 2
    assert {m["kind"] for m in q[esc]["media"]} >= {"fundus", "vessel", "artery_vein", "disc"}
    img = world.get(f"/media/{q[esc]['media'][0]['id']}")
    assert img.status_code == 200 and img.content.startswith(b"\x89PNG")
    assert world.post(f"/cases/{esc}/sign", json={"decision": "confirm", "crao": False}).status_code == 200
    assert world.post(f"/cases/{scr}/sign", json={"decision": "confirm"}).status_code == 403  # not escalated


def test_other_clinicians_and_admins_cannot_sign(world):
    rid = world.case()
    login(world, "gp2")
    assert world.post(f"/cases/{rid}/sign", json={"decision": "confirm", "crao": False}).status_code == 403
    login(world, "admin1")
    assert world.post(f"/cases/{rid}/sign", json={"decision": "confirm", "crao": False}).status_code == 403


def test_amendment_sets_amended_and_keeps_history(world):
    rid = world.case()
    world.post(f"/cases/{rid}/sign", json={"decision": "confirm", "crao": False})
    assert world.post(f"/cases/{rid}/sign", json={"decision": "confirm", "crao": False}).status_code == 409
    r = world.post(f"/cases/{rid}/amend", json={"finding": "BRAO, not CRAO", "reason_text": "OCT reviewed"})
    assert r.json()["status"] == "amended"
    h = world.get(f"/cases/{rid}/history").json()
    assert [v["status"] for v in sorted(h, key=lambda v: int(v["version"]))] == ["preliminary", "final", "amended"]
    assert world.get(f"/cases/{rid}/summary").json()["text"][0] == templates("en")["summary.override"]


def test_gp_reads_only_own_cases_reviewer_only_escalated_admin_no_images(world):
    esc, scr = world.case("emergency"), world.case("screening")
    fundus = next(x["id"] for x in world.get(f"/cases/{esc}").json()["media"] if x["kind"] == "fundus")
    scr_img = next(x["id"] for x in world.get(f"/cases/{scr}").json()["media"] if x["kind"] == "fundus")
    login(world, "gp2")  # another GP: nothing of gp1's
    for path in (f"/cases/{esc}", f"/cases/{esc}/history", f"/media/{fundus}"):
        assert world.get(path).status_code == 403, path
    assert world.post(f"/cases/{esc}/incident", json={"description": "x"}).status_code == 403
    login(world, "oph1")  # reviewer: escalated yes, other cases no
    assert world.get(f"/cases/{esc}").status_code == 200 and world.get(f"/media/{fundus}").status_code == 200
    assert world.get(f"/cases/{scr}").status_code == 403 and world.get(f"/media/{scr_img}").status_code == 403
    login(world, "admin1")
    assert world.get(f"/media/{fundus}").status_code == 403 and world.get(f"/cases/{esc}").status_code == 403


def test_blank_texts_are_refused(world):
    rid = world.case()
    r = world.post(f"/cases/{rid}/sign", json={"decision": "override", "finding": "not CRAO", "reason": "other",
                                                "reason_text": "   ", "crao": False})
    assert r.status_code == 422
    world.post(f"/cases/{rid}/sign", json={"decision": "confirm", "crao": False})
    for body in ({"finding": "", "reason_text": "x"}, {"finding": "x", "reason_text": "  "}):
        assert world.post(f"/cases/{rid}/amend", json=body).status_code == 422


def test_seeded_report_without_ai_code_gets_the_clinician_led_summary(fhir, monkeypatch):
    """HN-0001's seeded prior screening has no conclusionCode (it used to raise AttributeError -> 500)."""
    from fhir import mapping as m
    from routes.review import summary_key
    [p] = fhir.search("Patient", identifier=f"{m.MRN}|HN-0001")
    [rep] = fhir.search("DiagnosticReport", subject=f"Patient/{p['id']}")
    assert "conclusionCode" not in rep
    monkeypatch.setattr(deps, "fhir", lambda: fhir)  # mode_of reads the seeded Encounter
    assert summary_key(rep) == "summary.override"
