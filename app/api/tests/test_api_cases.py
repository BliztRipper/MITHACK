"""5.3/5.4: consent gate on upload; POST /cases end to end for each mode and for a RETAKE image.

AutoMorph is replaced by a fake segmentation (the real one takes ~30 s; tests/test_segment.py covers it).
"""
import base64
import io
import json
import logging

import cv2
import numpy as np
import pytest
import torch
from PIL import Image
from skimage import data as skdata

import analysis
import deps
from conftest import login
from fhir import mapping as m
from fhir.client import FhirUnavailable
from rules.text import templates
from vision import crao_model, segment

SAMPLE = (segment.AUTOMORPH / "images" / "100.png").read_bytes()  # AutoMorph sample fundus (Apache-2.0)
EMERGENCY = '{"hours_since_onset": 2, "sudden_painless_monocular": true, "gca_symptoms": false}'
SCREENING = {"age": 60, "sex": "male", "smoking": "current", "sbp": 150, "dbp": 85, "tc": 220, "hdl": 45, "ldl": 140,
             "diabetes": False, "treated_htn": False, "ascvd": False, "african_american": False}
CONSENT = {"care": True, "model_improvement": False, "retention_years": 10, "right_to_withdraw_explained": True}
EN = templates("en")


def fake_seg(rgb, features=True):
    h, w = rgb.shape[:2]
    vessel, disc = np.zeros((h, w, 4), np.uint8), np.zeros((h, w, 4), np.uint8)
    cv2.line(vessel, (w // 4, h // 2), (3 * w // 4, h // 2), (255, 220, 0, 255), 9)
    centre, dd = (w * 0.7, h * 0.5), h / 8
    cv2.circle(disc, (int(centre[0]), int(centre[1])), int(dd / 2), (0, 230, 120, 255), -1)
    return segment.Segmentation(True, vessel, vessel.copy(), disc, centre, dd, crae=140.0, crve=230.0, avr=0.61)


def png_bytes(rgb):
    buf = io.BytesIO()
    Image.fromarray(rgb).save(buf, "PNG")
    return buf.getvalue()


def dark_sample():
    rgb = np.array(Image.open(io.BytesIO(SAMPLE)).convert("RGB"))
    return png_bytes((rgb * 0.4).astype(np.uint8))


class Store:
    """Record store stand-in: care consent on file; down=True fails every write (store lost mid-request)."""
    def __init__(self, consent=True, down=False):
        self.consent, self.down, self.created, self.transactions = consent, down, [], []

    def read(self, rtype, rid):
        assert rtype == "Patient"
        return {"resourceType": "Patient", "id": rid}

    def search(self, rtype, **kw):
        assert rtype == "Consent"
        return [m.consent("Patient/p1", "care")] if self.consent else []

    def create(self, r, if_none_exist=None):
        if self.down:
            raise FhirUnavailable("record store unavailable")
        self.created.append(r)
        return {**r, "id": "7"}

    def transaction(self, es):
        if self.down:
            raise FhirUnavailable("record store unavailable")
        self.transactions.append(es)
        return {"entry": [{"response": {"location": f"{e['resource']['resourceType']}/{n}/_history/1"}} for n, e in enumerate(es)]}


@pytest.fixture
def stub(api, monkeypatch):
    monkeypatch.setattr(segment, "segment", fake_seg)
    monkeypatch.setattr(deps, "model", lambda: None)
    login(api, "gp1")
    return api


def use(api, monkeypatch, store):
    monkeypatch.setattr(deps, "fhir", lambda: store)
    api.store = store
    return store


def post(api, mode="emergency", inputs=EMERGENCY, image=SAMPLE, pid="p1", name="fundus.png"):
    return api.post("/cases", data={"patient_id": pid, "mode": mode, "inputs": inputs}, files={"image": (name, image)})


def no_seg(*a, **k):
    raise AssertionError("no model may run on a rejected image")


# --- consent gate (5.3) -------------------------------------------------------------------------------

@pytest.mark.fhir
def test_upload_refused_without_consent_then_allowed_after_consent(live, fhir, patient, monkeypatch):
    monkeypatch.setattr(segment, "segment", fake_seg)
    monkeypatch.setattr(deps, "model", lambda: None)
    login(live, "gp1")
    r = post(live, pid=patient)
    assert r.status_code == 403 and r.json()["detail"]["code"] == "consent_required"
    assert fhir.search("Media", subject=f"Patient/{patient}") == []  # nothing stored
    live.post(f"/patients/{patient}/consent", json=CONSENT)
    r = post(live, pid=patient)
    assert r.status_code == 200 and r.json()["saved"]


def test_unsupported_and_oversize_files_rejected_with_reason(stub, monkeypatch):
    s = use(stub, monkeypatch, Store())
    r = post(stub, image=b"%PDF-1.4 not an image", name="x.pdf")
    assert r.status_code == 400 and r.json()["detail"] == "only JPEG or PNG images are accepted"
    r = post(stub, image=b"\x89PNG\r\n\x1a\n" + b"0" * (30 * 1024 * 1024))
    assert r.status_code == 400 and r.json()["detail"] == "file is larger than 20 MB"
    assert s.transactions == []


def test_implausible_value_rejected_naming_the_range(stub, monkeypatch):
    use(stub, monkeypatch, Store())
    r = post(stub, "screening", '{"age": 60, "sex": "male", "smoking": "never", "sbp": 400, "diabetes": false, "treated_htn": false, "ascvd": false, "african_american": false}')
    assert r.status_code == 422
    [err] = r.json()["detail"]
    assert err["loc"][-1] == "sbp" and "260" in err["msg"]
    r = post(stub, "screening", '{"age": 60, "sex": "male", "smoking": "never", "sbp": 120, "tc": 5, "diabetes": false, "treated_htn": false, "ascvd": false, "african_american": false}')
    assert r.status_code == 422 and "50" in r.json()["detail"][0]["msg"]


# --- Emergency ------------------------------------------------------------------------------------------

@pytest.mark.fhir
def test_emergency_no_model_end_to_end_saved_as_preliminary(live, fhir, patient, monkeypatch):
    monkeypatch.setattr(segment, "segment", fake_seg)
    monkeypatch.setattr(deps, "model", lambda: None)
    login(live, "gp1")
    live.post(f"/patients/{patient}/consent", json=CONSENT)
    r = post(live, pid=patient).json()
    assert r["status"] == "preliminary" and r["label"] == "AI-assisted, not a diagnosis"
    assert r["quality"]["accept"] and 0 < r["quality"]["score"] <= 1
    assert r["crao"]["status"] == "no model loaded" and r["crao"]["probability"] is None
    assert r["triage"]["level"] == "ESCALATE" and r["triage"]["reasons"]
    assert r["explanation"]["sentences"][0] == EN["explain.emergency.no_model"]
    assert all(r["overlays"][k] for k in ("vessel", "artery_vein", "disc")) and r["overlays"]["heatmap"] is None
    assert r["saved"] and r["save_error"] is None
    rep = fhir.read("DiagnosticReport", r["report_id"])
    assert rep["status"] == "preliminary" and rep["conclusionCode"][0]["coding"][0]["code"] == "ESCALATE"
    assert rep["category"][0]["coding"][0]["code"] == "emergency"
    media = fhir.search("Media", subject=f"Patient/{patient}")
    assert len(media) == 4  # fundus + vessel, A/V and disc overlays
    for med in media:
        assert not base64.b64decode(med["content"]["data"]).startswith(b"\x89PNG")  # ciphertext only
    codes = {o["code"]["coding"][0]["code"] for o in fhir.search("Observation", subject=f"Patient/{patient}")}
    assert {"hours-since-vision-loss", "sudden-painless-monocular-loss", "gca-symptoms", "image-quality-score"} <= codes
    [ev] = fhir.search("AuditEvent", entity=f"DiagnosticReport/{r['report_id']}")
    assert ev["action"] == "C" and ev["agent"][0]["who"]["display"] == "gp1"


def test_emergency_with_a_model_band_and_triage_use_the_same_thresholds(stub, monkeypatch, tmp_path):
    net = crao_model.build("efficientnet_b0", pretrained=False)
    torch.save({"arch": "efficientnet_b0", "state": net.state_dict(), "version": "test-2", "temperature": 1.5,
                "p_low": 0.2, "p_high": 0.6, "calibration_date": "2026-10-17"}, tmp_path / "m.pt")
    model = crao_model.load(tmp_path / "m.pt", "cpu")
    monkeypatch.setattr(deps, "model", lambda: model)
    s = use(stub, monkeypatch, Store())
    r = post(stub).json()
    c = r["crao"]
    assert c["status"] == "ok" and 0 <= c["probability"] <= 1 and (c["p_low"], c["p_high"]) == (0.2, 0.6)
    assert c["band"] == crao_model.band(c["probability"], 0.2, 0.6)
    expected = {"likely": {"STROKE_PATHWAY"}, "uncertain": {"ESCALATE"}, "unlikely": {"ESCALATE", "ROUTINE"}}
    assert r["triage"]["level"] in expected[c["band"]]
    assert c["model"]["version"] == "test-2" and c["model"]["calibration_date"] == "2026-10-17"
    assert r["overlays"]["heatmap"] and r["explanation"]["region"] in ("macula", "optic_disc", "arcades", "periphery")
    assert EN["limit.heatmap_attention"] in r["explanation"]["sentences"]
    [es] = s.transactions
    dev = es[0]["resource"]
    assert dev["resourceType"] == "Device" and dev["version"][0]["value"] == "test-2"
    assert sum(e["resource"]["resourceType"] == "Media" for e in es) == 5  # + heatmap overlay


def test_retake_image_runs_no_model_and_keeps_urgent_referral(stub, monkeypatch):
    monkeypatch.setattr(segment, "segment", no_seg)
    model = type("M", (), {"info": lambda s: {"model": "stub", "version": "x", "calibration_date": None}, "thresholds": lambda s: (0.3, 0.7), "probability": no_seg})()
    monkeypatch.setattr(deps, "model", lambda: model)
    use(stub, monkeypatch, Store())
    r = post(stub, image=dark_sample()).json()
    assert not r["quality"]["accept"] and any(x.startswith("underexposed") for x in r["quality"]["reasons"])
    assert r["triage"]["level"] == "RETAKE"
    assert any("do not delay referral" in a for a in r["triage"]["actions"])
    assert r["crao"]["probability"] is None and r["crao"]["status"] == "not run: image failed the quality gate"
    assert r["segmentation"] is None
    assert r["overlays"] == {"vessel": None, "artery_vein": None, "disc": None, "heatmap": None}


def test_non_fundus_image_refused_as_not_a_fundus_image(stub, monkeypatch):
    monkeypatch.setattr(segment, "segment", no_seg)
    use(stub, monkeypatch, Store())
    r = post(stub, image=png_bytes(skdata.astronaut())).json()
    assert r["quality"]["reasons"] == ["not a fundus image"] and r["triage"]["level"] == "RETAKE"


# --- Screening ----------------------------------------------------------------------------------------

@pytest.mark.fhir
def test_screening_end_to_end_with_retinal_enhancer(live, fhir, patient, monkeypatch):
    monkeypatch.setattr(segment, "segment", fake_seg)
    monkeypatch.setattr(deps, "model", lambda: None)
    login(live, "gp1")
    live.post(f"/patients/{patient}/consent", json=CONSENT)
    import json
    r = post(live, "screening", json.dumps(SCREENING), pid=patient).json()
    pce = r["risk"]["pce"]
    assert pce["label"] == "PCE (white)" and pce["risk"] > 0 and pce["band"] and pce["suggestion"]
    assert pce["notes"] == [EN["risk.caveat.pce_not_asian"]]
    assert set(r["risk"]) == {"pce", "bypass", "htn_stage1", "enhancers", "arcus"}
    avr = r["measurements"]["avr"]
    assert avr["value"] == 0.61 and avr["flag"] == "outside reference"
    assert r["risk"]["enhancers"]["retinal"] == [EN["risk.enhancer.retinal_arteriolar_narrowing.placeholder"]]
    assert "placeholder" in r["explanation"]["sentences"][0] and "0.61: outside" in r["explanation"]["sentences"][0]
    for k in ("crae", "crve"):
        assert r["measurements"][k]["flag"] == "not_assessed"
        assert r["measurements"][k]["reason"] == "camera-dependent pixel scale"
    assert r["explanation"]["sentences"][-1] == EN["limit.screening.not_diagnostic"]
    assert r["saved"] and r["status"] == "preliminary"
    [ra] = fhir.search("RiskAssessment", subject=f"Patient/{patient}")
    assert ra["method"]["text"] == "PCE (white)"
    assert fhir.read("DiagnosticReport", r["report_id"])["status"] == "preliminary"


def test_screening_failed_quality_still_computes_risk_without_retinal_enhancers(stub, monkeypatch):
    import json
    use(stub, monkeypatch, Store())
    r = post(stub, "screening", json.dumps(SCREENING), image=dark_sample()).json()
    assert r["risk"]["pce"]["risk"] > 0 and r["measurements"] is None
    assert r["risk"]["enhancers"]["not_assessed"] == EN["risk.retinal_not_assessed"]


@pytest.mark.parametrize("extra", [{"ascvd": True}, {"ldl": 195}])
def test_statin_benefit_group_gets_no_primary_prevention_suggestion(stub, monkeypatch, extra):
    import json
    use(stub, monkeypatch, Store())
    r = post(stub, "screening", json.dumps({**SCREENING, **extra}))
    body = r.json()
    assert body["risk"]["pce"]["suggestion"] is None and body["risk"]["enhancers"]["note"] is None
    assert body["risk"]["bypass"] == EN["risk.bypass.ascvd" if "ascvd" in extra else "risk.bypass.ldl190"]
    for k, v in EN.items():
        if k.startswith("risk.suggestion."):
            assert v not in r.text


@pytest.mark.parametrize("extra,key", [({"diabetes": True}, "risk.bypass.diabetes"),
                                       ({"diabetes": True, "ldl": None}, "risk.bypass.diabetes.no_ldl")])
def test_diabetes_40_75_states_statin_group_and_labels_pce_as_intensity_only(stub, monkeypatch, extra, key):
    import json
    use(stub, monkeypatch, Store())
    b = post(stub, "screening", json.dumps({**SCREENING, **extra})).json()["risk"]
    assert b["bypass"] == EN[key] and b["pce"]["suggestion"] is None and b["enhancers"]["note"] is None
    assert b["pce"]["risk"] > 0 and b["pce"]["intensity_only"] == EN["risk.pce_intensity_only"]


@pytest.mark.parametrize("field", ["diabetes", "treated_htn", "ascvd", "african_american"])
def test_screening_requires_explicit_yes_no_inputs(stub, field):
    r = post(stub, "screening", json.dumps({k: v for k, v in SCREENING.items() if k != field}))
    assert r.status_code == 422 and field in r.text


def test_non_diabetic_has_no_intensity_only_label_and_age_35_shows_out_of_range_text(stub, monkeypatch):
    import json
    use(stub, monkeypatch, Store())
    ok = post(stub, "screening", json.dumps(SCREENING)).json()["risk"]["pce"]
    assert ok["intensity_only"] is None and ok["suggestion"]
    b = post(stub, "screening", json.dumps({**SCREENING, "age": 35})).json()
    assert b["risk"]["pce"]["risk"] is None and b["risk"]["pce"]["not_valid"] == EN["risk.not_valid.pce_age"]
    assert "outside validated age range (40–79)" in b["conclusion"]


# --- record store down / analysis failure --------------------------------------------------------------

def test_record_store_down_returns_analysis_unsaved_with_no_partial_save(stub, monkeypatch):
    s = use(stub, monkeypatch, Store(down=True))
    r = post(stub)
    body = r.json()
    assert r.status_code == 200 and body["triage"]["level"] == "ESCALATE" and body["overlays"]["vessel"]
    assert body["saved"] is False and body["report_id"] is None
    assert body["save_error"] == "record store unavailable, not saved"
    assert s.transactions == [] and s.created == []


@pytest.mark.parametrize("err", [segment.SegmentationError("AutoMorph run.sh exited 1:\n/Users/x/automorph/M2 failed"),
                                 RuntimeError("AutoMorph produced no M2 masks:\n/Users/x/automorph/log")])
def test_segmentation_failure_is_a_generic_server_error(stub, monkeypatch, caplog, err):
    def boom(*a, **k):
        raise err
    monkeypatch.setattr(segment, "segment", boom)
    s = use(stub, monkeypatch, Store())
    with caplog.at_level(logging.ERROR, logger="api"):
        r = post(stub)
    assert r.status_code == 500 and r.json() == {"detail": "analysis service error"}
    assert "/Users" not in r.text and "retake" not in r.text.lower()
    [line] = [x.getMessage() for x in caplog.records if x.getMessage().startswith("analysis failed")]
    assert line.startswith("analysis failed case=") and type(err).__name__ in line
    assert s.transactions == []


# --- demo cache ------------------------------------------------------------------------------------------

def test_cache_hit_skips_the_pipeline(stub, monkeypatch, tmp_path):
    import hashlib
    monkeypatch.setattr(analysis, "CACHE", tmp_path)
    rgb = np.array(Image.open(io.BytesIO(SAMPLE)).convert("RGB"))
    analysis.cache_put(hashlib.sha256(SAMPLE).hexdigest(), *analysis.image_stage(rgb, None))
    monkeypatch.setattr(segment, "segment", no_seg)
    use(stub, monkeypatch, Store())
    r = post(stub).json()
    assert r["cached"] and r["triage"]["level"] == "ESCALATE" and r["overlays"]["vessel"]


@pytest.mark.slow
def test_emergency_with_real_automorph(api, monkeypatch):
    monkeypatch.setattr(deps, "model", lambda: None)
    use(api, monkeypatch, Store())
    login(api, "gp1")
    r = post(api).json()
    assert r["quality"]["accept"] and r["segmentation"]["disc_found"] and r["triage"]["level"] == "ESCALATE"


def test_patient_id_comma_injection_is_refused(stub, monkeypatch):
    s = use(stub, monkeypatch, Store())
    r = post(stub, pid="X,Patient/123")
    assert r.status_code == 422 and s.transactions == []
    assert stub.get("/media/1,2").status_code == 422 and stub.get("/cases/a,b").status_code == 422


@pytest.mark.fhir
def test_unknown_patient_is_404(live, monkeypatch):
    monkeypatch.setattr(segment, "segment", fake_seg)
    login(live, "gp1")
    assert post(live, pid="99999999").status_code == 404
