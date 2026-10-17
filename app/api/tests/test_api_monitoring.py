"""5.6: metrics per version, calibration minimum, rolling-50 drift alerts with acknowledge, incidents,
de-identified consented export (spec: model-monitoring)."""
import csv
import io
import logging
import zipfile

import pytest

import deps
from conftest import login, purge
from fhir import mapping as m
from routes import monitoring as mon
from test_api_cases import CONSENT, fake_seg, post
from vision import segment


def rows(n, version="v1", mode="emergency", band="likely", decision="confirm", accept=True, **kw):
    return [{"id": str(i), "version": version, "mode": mode, "issued": f"2026-10-17T10:{i // 60:02d}:{i % 60:02d}+00:00",
             "accept": accept, "band": band if mode == "emergency" else None, "p": 0.8, "level": "URGENT",
             "signed": decision is not None, "decision": decision, "reason": kw.get("reason"), "crao": kw.get("crao", True)}
            for i in range(n)]


# --- pure rules ---------------------------------------------------------------------------------------

def test_metrics_are_per_version_with_case_counts():
    rs = rows(3, "v1") + rows(2, "v2", accept=False, decision=None) + rows(1, "v2", mode="screening", decision=None)
    v1, v2 = mon.metrics(rs)
    assert v1["version"] == "v1" and v1["cases"] == 3 and v1["agreement_rate"] == {"value": 1.0, "n": 3}
    assert v2["cases"] == 3 and v2["by_mode"] == {"emergency": 2, "screening": 1}
    assert v2["quality_rejection_rate"] == {"value": 0.667, "n": 3} and v2["agreement_rate"] == {"value": None, "n": 0}
    assert v1["triage_levels"] == {"URGENT": 3}


def test_calibration_needs_30_signed_emergency_cases():
    assert mon.calibration(rows(12), "v1")["text"] == "insufficient data (12 of 30)"
    # signed but band-less cases (no model loaded, quality rejected) do not count toward the 30
    assert mon.calibration(rows(12) + rows(40, band=None), "v1")["text"] == "insufficient data (12 of 30)"
    cal = mon.calibration(rows(30) + rows(5, band="unlikely", crao=False), "v1")
    assert cal["status"] == "ok" and cal["bands"]["likely"] == {"n": 30, "mean_p": 0.8, "observed_crao_rate": 1.0}
    assert cal["bands"]["unlikely"]["observed_crao_rate"] == 0.0


def test_override_spike_alert():
    rs = rows(35) + rows(15, decision="override", reason="image misread")
    [a] = mon.drift(rs)
    assert a["metric"] == "override_rate" and a["value"] == 0.3 and a["limit"] == 0.2


def test_rubber_stamping_alert():
    [a] = mon.drift(rows(50))
    assert a["metric"] == "agreement_rate" and "automation bias" in a["message"]


def test_quality_and_uncertain_alerts_and_no_alert_before_the_window_fills():
    assert mon.drift(rows(49)) == []  # 49 of 49 confirmed: window not full yet
    metrics = {a["metric"] for a in mon.drift(rows(50, accept=False, band="uncertain", decision=None))}
    assert metrics == {"quality_rejection_rate", "uncertain_rate"}


# --- endpoints ---------------------------------------------------------------------------------------

@pytest.fixture
def world(live, fhir, patient, monkeypatch):
    monkeypatch.setattr(segment, "segment", fake_seg)
    monkeypatch.setattr(deps, "model", lambda: None)
    login(live, "gp1")
    live.post(f"/patients/{patient}/consent", json=CONSENT)
    live.patient = patient
    return live


@pytest.mark.fhir
def test_dashboard_roles_and_metrics(world):
    assert world.get("/monitoring").status_code == 403  # gp
    post(world, pid=world.patient)
    login(world, "oph1")
    d = world.get("/monitoring", params={"days": 30}).json()
    assert d["period_days"] == 30 and d["current_version"] == "no-model"
    [v] = [x for x in d["metrics"] if x["version"] == "no-model"]
    assert v["cases"] >= 1 and v["by_mode"]["emergency"] >= 1 and v["quality_rejection_rate"]["n"] == v["cases"]
    assert d["calibration"]["status"] == "insufficient data"
    login(world, "admin1")
    assert world.get("/monitoring").status_code == 200


@pytest.mark.fhir
def test_drift_flag_logged_shown_until_acknowledged_with_a_note(world, caplog):
    rs = rows(35, "no-model") + rows(15, "no-model", decision="override", reason="image misread")
    with caplog.at_level(logging.WARNING, logger="api"):
        mon.check_drift(rs)
    assert "drift alert version=no-model metric=override_rate" in caplog.text
    mon.check_drift(rs)  # still open: not raised twice
    login(world, "admin1")
    [a] = world.get("/monitoring").json()["alerts"]
    assert a["metric"] == "override_rate" and "15/50" in a["text"]
    assert world.post(f"/monitoring/alerts/{a['id']}/acknowledge", json={"note": " "}).status_code == 422
    r = world.post(f"/monitoring/alerts/{a['id']}/acknowledge", json={"note": "reviewed with the GP team"})
    assert r.json()["status"] == "inactive"
    mon.check_drift(rs)  # same window, already acknowledged: no new alert
    assert world.get("/monitoring").json()["alerts"] == []


@pytest.mark.fhir
def test_incident_flagged_by_clinician_listed_until_closed(world, patient):
    rid = post(world, pid=patient).json()["report_id"]
    world.post(f"/cases/{rid}/sign", json={"decision": "confirm", "crao": False})
    r = world.post(f"/cases/{rid}/incident", json={"description": "missed CRAO later confirmed"})
    assert r.status_code == 200
    login(world, "admin1")
    [i] = world.get("/monitoring").json()["incidents"]
    assert i["text"] == "missed CRAO later confirmed" and i["case"] == f"DiagnosticReport/{rid}"
    world.post(f"/monitoring/incidents/{i['id']}/close", json={"note": "root cause reviewed"})
    assert world.get("/monitoring").json()["incidents"] == []


@pytest.mark.fhir
def test_export_holds_only_consented_signed_cases_de_identified_and_audited(world, fhir, patient):
    other = fhir.create(m.patient("TEST-API-care-only", "Testapi", "Malee", "female", "1955-02-02"))["id"]
    try:
        world.post(f"/patients/{other}/consent", json=CONSENT)  # care only
        world.post(f"/patients/{patient}/consent", json={**CONSENT, "model_improvement": True})
        keep = post(world, pid=patient).json()["report_id"]
        drop = post(world, pid=other).json()["report_id"]
        post(world, pid=patient)  # unsigned: excluded
        for rid in (keep, drop):
            world.post(f"/cases/{rid}/sign", json={"decision": "override", "finding": "not CRAO",
                                                    "reason": "clinical findings disagree", "crao": False})
        login(world, "admin1")
        r = world.get("/monitoring/export")
        z = zipfile.ZipFile(io.BytesIO(r.content))
        labels = list(csv.DictReader(io.StringIO(z.read("labels.csv").decode())))
        mine = [x for x in labels if x["file"] in z.namelist()]
        assert len(mine) == len(labels) and len(labels) >= 1
        x = labels[0]
        assert (x["decision"], x["crao_confirmed"], x["ai_code"], x["model_version"]) == ("override", "False", "ESCALATE", "no-model")
        assert "not CRAO" not in z.read("labels.csv").decode()  # never the clinician's free text
        from PIL import Image
        im = Image.open(io.BytesIO(z.read(x["file"])))
        assert im.format == "PNG" and not im.info and "exif" not in im.info  # re-encoded: no metadata chunks
        blob = z.read("labels.csv").decode() + " ".join(z.namelist())
        for ident in ("Testapi", "Somsri", "Malee", "TEST-API", "1960-01-01", "1955-02-02"):
            assert ident not in blob
        assert len(labels) == 1  # the care-only patient and the unsigned case are excluded
        [ev] = [a for a in fhir.search("AuditEvent", action="E") if a["agent"][0]["who"]["display"] == "admin1"]
        assert [e["what"]["reference"] for e in ev["entity"]] == [f"DiagnosticReport/{keep}"]
    finally:
        purge(fhir, other)


def test_audit_has_no_write_routes_and_is_admin_only(api):
    login(api, "gp1")
    assert api.get("/audit").status_code == 403
    for method in ("put", "patch", "delete", "post"):
        assert getattr(api, method)("/audit").status_code == 405


class FlagStore:
    def __init__(self, flags):
        self.flags, self.created = flags, []

    def search(self, rtype, **kw):
        return self.flags

    def create(self, r, if_none_exist=None):
        self.created.append(r)
        return {**r, "id": "1"}


def test_drift_dedupe_matches_the_exact_model_version(monkeypatch):
    model = type("M", (), {"info": lambda s: {"model": "m", "version": "v1", "calibration_date": None}})()
    monkeypatch.setattr(deps, "model", lambda: model)
    v10 = {"status": "active", "category": [{"coding": [{"code": "drift"}]}],
           "code": {"text": "[v10] …", "coding": [{"system": m.LOCAL, "code": "override_rate"},
                                                  {"system": mon.VERSION_SYSTEM, "code": "v10"}]}}
    s = FlagStore([v10])
    monkeypatch.setattr(deps, "fhir", lambda: s)
    rs = rows(35, "v1") + rows(15, "v1", decision="override", reason="image misread")
    mon.check_drift(rs)
    [flag] = [r for r in s.created if r["resourceType"] == "Flag"]  # v10's open flag does not hide v1's alert
    assert mon._coded(flag, mon.VERSION_SYSTEM) == "v1"
    s.flags, s.created = [flag], []
    mon.check_drift(rs)
    assert [r for r in s.created if r["resourceType"] == "Flag"] == []  # same version already open


def test_flag_ids_are_validated(api):
    login(api, "admin1")
    for path in ("/monitoring/alerts/1,2/acknowledge", "/monitoring/incidents/1,2/close"):
        assert api.post(path, json={"note": "x"}).status_code == 422
    assert api.post("/monitoring/alerts/1%2F2/acknowledge", json={"note": "x"}).status_code in (404, 422)
