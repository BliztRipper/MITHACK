"""live-demo-deployment group 1: the API as a public demo (DEMO_MODE=1)."""
import hashlib
import os
import subprocess
import sys
import time

import pytest

import analysis
import deps
from conftest import login

ML = ("torch", "torchvision", "timm", "cv2", "pytorch_grad_cam", "efficientnet_pytorch")


def test_import_main_loads_no_ml_stack():
    """1.1: with no model configured, the API (and a cached analysis) imports neither torch nor OpenCV."""
    code = ("import sys, json, main, analysis, routes.monitoring\n"
            "from fhir import seed\n"
            "img = json.loads((analysis.CACHE / '33c3877c97c56ec2845cd339e1bea4becb65c4b64f24a424254d3854318e9f38' / 'meta.json').read_text())\n"
            "assert analysis.cache_get('33c3877c97c56ec2845cd339e1bea4becb65c4b64f24a424254d3854318e9f38', main.deps.model())\n"
            "analysis.emergency(img, {}, 2, True, False, None)\n"
            f"print(sorted(m for m in {ML!r} if m in sys.modules))\n")
    env = {k: v for k, v in os.environ.items() if k != "CRAO_MODEL"} | {"DEMO_MODE": "1"}
    out = subprocess.run([sys.executable, "-c", code], cwd=deps.API, env=env, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "[]"

CONSENT = {"care": True, "model_improvement": False, "retention_years": 10, "right_to_withdraw_explained": True}
EMERGENCY = '{"hours_since_onset": 2, "sudden_painless_monocular": true, "gca_symptoms": false}'
SCREENING = ('{"age": 60, "sex": "male", "smoking": "never", "sbp": 135, "tc": 210, "hdl": 50, "diabetes": false, '
             '"treated_htn": false, "ascvd": false, "african_american": false}')
CURATED = analysis.CACHE / "images" / "rao_rfmid_716.png"  # sha 33c3877c...: a cached RAO case
UNKNOWN = b"\x89PNG\r\n\x1a\n" + b"not one of the demo photos"


@pytest.fixture
def demo(monkeypatch):
    monkeypatch.setattr(deps, "DEMO", True)
    monkeypatch.setattr(deps, "model", lambda: None)


def post_case(client, pid, image, name="x.png", mode="emergency"):
    return client.post("/cases", data={"patient_id": pid, "mode": mode, "inputs": EMERGENCY if mode == "emergency" else SCREENING},
                       files={"image": (name, image)})


def test_demo_refuses_unknown_photo_before_consent_or_storage(api, demo):
    """1.2: the Recorder store fails any consent read or save; only the request's AuditEvent may be written."""
    login(api, "gp1")
    r = post_case(api, "p1", UNKNOWN)
    assert r.status_code == 422 and r.json()["detail"]["code"] == "demo_photo_only", r.text
    assert [x["resourceType"] for x in api.store.created] == ["AuditEvent"]
    assert "not one of the demo photos" not in str(api.store.created)


def test_health_reports_demo_mode(monkeypatch):
    from fastapi.testclient import TestClient
    import main

    class Up:
        def health_check(self):
            return True
    monkeypatch.setattr(deps, "fhir", lambda: Up())
    c = TestClient(main.app)
    assert c.get("/health").json() == {"api": "ok", "record_store": "available", "demo": False}
    monkeypatch.setattr(deps, "DEMO", True)
    assert c.get("/health").json()["demo"] is True


@pytest.mark.fhir
@pytest.mark.skipif(not CURATED.exists(), reason="run python -m demo_cache.build first (needs the local data/ copies)")
@pytest.mark.parametrize("mode", ["emergency", "screening"])
def test_demo_curated_photo_returns_cached_result_fast(live, patient, demo, monkeypatch, mode):
    monkeypatch.setattr(analysis, "CACHE", CURATED.parents[1])
    login(live, "gp1")
    live.post(f"/patients/{patient}/consent", json=CONSENT)
    raw = CURATED.read_bytes()
    assert hashlib.sha256(raw).hexdigest().startswith("33c3877c")
    t = time.perf_counter()
    r = post_case(live, patient, raw, CURATED.name, mode)
    took = time.perf_counter() - t
    assert r.status_code == 200 and r.json()["cached"] and r.json()["saved"], r.text
    assert took < 2.0, f"{took:.2f} s"


@pytest.mark.fhir
def test_demo_unknown_photo_creates_no_fhir_resources(live, patient, demo):
    login(live, "gp1")
    live.post(f"/patients/{patient}/consent", json=CONSENT)
    before = {t: len(live.store.search(t, subject=f"Patient/{patient}")) for t in ("Media", "DiagnosticReport", "Encounter")}
    r = post_case(live, patient, UNKNOWN)
    assert r.status_code == 422 and r.json()["detail"]["code"] == "demo_photo_only"
    assert {t: len(live.store.search(t, subject=f"Patient/{patient}")) for t in before} == before


@pytest.mark.fhir
def test_demo_off_unknown_photo_still_reaches_the_consent_gate(live, patient, monkeypatch):
    monkeypatch.setattr(deps, "model", lambda: None)
    login(live, "gp1")
    r = post_case(live, patient, UNKNOWN)
    assert r.status_code == 403 and r.json()["detail"]["code"] == "consent_required"


def test_demo_images_lists_the_six_curated_photos_with_credits(api):
    """1.3: built from demo_cache/SOURCES.md; each entry names its source and licence."""
    items = api.get("/demo-images").json()
    assert len(items) == 6
    assert {i["name"] for i in items} >= {"rao_rfmid_716.png", "normal_nei_eda06.jpg", "mimic_brvo_ku2011.jpg"}
    assert all(i["label"] and i["source"] and i["licence"] for i in items)
    assert next(i for i in items if i["name"] == "mimic_brvo_ku2011.jpg")["licence"] == "CC BY 2.0"


@pytest.mark.skipif(not CURATED.exists(), reason="run python -m demo_cache.build first (needs the local data/ copies)")
def test_demo_image_served_by_exact_name(api):
    r = api.get(f"/demo-images/{CURATED.name}")
    assert r.status_code == 200 and r.content == CURATED.read_bytes() and r.headers["content-type"] == "image/png"


@pytest.mark.parametrize("name", ["SOURCES.md", "build.py", "x.png", "..%2FSOURCES.md", "..%2F..%2Fusers.yaml",
                                  "%2E%2E%2Fmain.py", "rao_rfmid_716.PNG", "images%2Frao_rfmid_716.png"])
def test_demo_image_unlisted_or_traversal_is_404(api, name):
    assert api.get(f"/demo-images/{name}").status_code == 404
