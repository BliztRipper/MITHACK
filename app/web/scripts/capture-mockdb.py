"""Record a running demo API into the browser test DB (public/mockdb/) that src/mockdb.ts serves when /api is down.

Run with the API venv against a local demo API (DEMO_MODE=1, users.demo.yaml, local IRIS):
    ../api/.venv/bin/python scripts/capture-mockdb.py http://localhost:8765 gp1:PW oph1:PW admin1:PW
Creates one case per demo photo and mode (the templates New Case returns; reused from an existing db.json on a re-run),
then records every report and its media (stored once per content hash).
"""
import hashlib
import json
import pathlib
import sys

import httpx

WEB = pathlib.Path(__file__).resolve().parents[1]
API_DIR = WEB.parent / "api"
sys.path.insert(0, str(API_DIR))
from fhir.client import FhirClient  # noqa: E402  (lists patient ids; the API has no list endpoint)

OUT = WEB / "public" / "mockdb"
SCREENING = {"age": 60, "sex": "male", "smoking": "current", "sbp": 150, "dbp": 85, "tc": 220, "hdl": 45, "ldl": 140,
             "african_american": False, "ascvd": False}
EMERGENCY = {"hours_since_onset": 2, "sudden_painless_monocular": True, "gca_symptoms": False}


def client(base: str, cred: str) -> httpx.Client:
    c = httpx.Client(base_url=base, timeout=120)
    u, p = cred.split(":", 1)
    c.post("/auth/login", json={"username": u, "password": p}).raise_for_status()
    return c


def ok(r: httpx.Response):
    r.raise_for_status()
    return r.json()


def main(base: str, gp_cred: str, oph_cred: str, admin_cred: str):
    gp, oph, admin = client(base, gp_cred), client(base, oph_cred), client(base, admin_cred)
    (OUT / "media").mkdir(parents=True, exist_ok=True)
    (OUT / "demo-images").mkdir(exist_ok=True)

    images = ok(gp.get("/demo-images"))
    for img in images:
        (OUT / "demo-images" / img["name"]).write_bytes(gp.get(f"/demo-images/{img['name']}").raise_for_status().content)

    pids = [p["id"] for p in FhirClient().search("Patient")]
    consented = next(pid for pid in pids if ok(gp.get(f"/patients/{pid}/consent"))["care"])
    old = OUT / "db.json"
    results = json.loads(old.read_text())["results"] if old.exists() else {}  # "<image>|<mode>" -> POST /cases reply
    for img in images:
        for mode, inputs in (("screening", SCREENING), ("emergency", EMERGENCY)):
            if f"{img['name']}|{mode}" in results:
                continue
            data = (OUT / "demo-images" / img["name"]).read_bytes()
            r = ok(gp.post("/cases", data={"patient_id": consented, "mode": mode, "inputs": json.dumps(inputs)},
                           files={"image": (img["name"], data)}))
            r.pop("overlays", None)  # saved cases show overlays from their record's media instead
            results[f"{img['name']}|{mode}"] = r

    patients = {pid: ok(gp.get(f"/patients/{pid}")) for pid in pids}
    rids = {c["report_id"] for p in patients.values() for c in p["cases"]}
    rids |= {r["report_id"] for r in results.values() if r.get("report_id")}
    cases, media = {}, {}  # media: id -> file name under media/
    for rid in sorted(rids):
        who = next((x for x in (gp, oph) if x.get(f"/cases/{rid}").status_code == 200), None)
        if who is None:  # authored by a user outside the demo accounts: the app shows it as not readable
            continue
        rec = ok(who.get(f"/cases/{rid}"))
        cases[rid] = {"record": rec, "history": ok(who.get(f"/cases/{rid}/history")),
                      "summary": {lang: ok(who.get(f"/cases/{rid}/summary", params={"lang": lang})) for lang in ("en", "th")}}
        for m in rec["media"]:
            body = who.get(f"/media/{m['id']}").raise_for_status().content
            media[m["id"]] = hashlib.sha256(body).hexdigest()[:16]
            (OUT / "media" / media[m["id"]]).write_bytes(body)

    db = {
        "health": {**ok(gp.get("/health")), "record_store": "available"},
        "users": {c.split(":")[0]: ok(x.get("/auth/me")) for c, x in ((gp_cred, gp), (oph_cred, oph), (admin_cred, admin))},
        "demo_images": images,
        "about": ok(gp.get("/about")),
        "patients": patients,
        "results": results,
        "cases": cases,
        "media": media,
        "monitoring": ok(admin.get("/monitoring", params={"days": 30})),
        "audit": ok(admin.get("/audit", params={"days": 1})),
    }
    (OUT / "db.json").write_text(json.dumps(db, indent=1, ensure_ascii=False))
    print(f"{len(patients)} patients, {len(cases)} cases, {len(results)} case templates -> {OUT}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
