"""5.7: every demo-cache entry is attributed in SOURCES.md and returns via POST /cases in under 2 s."""
import hashlib
import time

import pytest

import analysis
import deps
from conftest import login
from test_api_cases import CONSENT

IMAGES = analysis.CACHE / "images"
ENTRIES = sorted(p.parent.name for p in analysis.CACHE.glob("*/meta.json"))


def test_every_cached_case_is_attributed():
    sources = (analysis.CACHE / "SOURCES.md").read_text()
    assert ENTRIES and all(sha in sources for sha in ENTRIES)


@pytest.mark.fhir
@pytest.mark.skipif(not IMAGES.exists(), reason="run python -m demo_cache.build first (needs the local data/ copies)")
def test_each_cached_case_returns_in_under_2_seconds(live, patient, monkeypatch):
    monkeypatch.setattr(deps, "model", lambda: None)
    monkeypatch.setattr(analysis.segment, "segment", lambda *a, **k: pytest.fail("cache miss: pipeline ran"))
    login(live, "gp1")
    live.post(f"/patients/{patient}/consent", json=CONSENT)
    files = {hashlib.sha256(p.read_bytes()).hexdigest(): p for p in IMAGES.glob("*.png")}
    assert set(ENTRIES) <= files.keys()
    for sha in ENTRIES:
        for mode, inputs in (("emergency", '{"hours_since_onset": 2, "sudden_painless_monocular": true, "gca_symptoms": false}'),
                             ("screening", '{"age": 60, "sex": "male", "smoking": "never", "sbp": 135, "tc": 210, "hdl": 50}')):
            t = time.perf_counter()
            r = live.post("/cases", data={"patient_id": patient, "mode": mode, "inputs": inputs},
                          files={"image": (files[sha].name, files[sha].read_bytes())})
            took = time.perf_counter() - t
            body = r.json()
            assert r.status_code == 200 and body["cached"] and body["saved"], files[sha].name
            assert took < 2.0, f"{files[sha].name} {mode}: {took:.2f} s"
            print(f"{files[sha].name} {mode} {took:.2f}s")
