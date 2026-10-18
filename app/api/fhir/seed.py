"""Load 20 synthetic Thai patients (no real data). Idempotent: every resource is a conditional create.

Run: FHIR_USER=... FHIR_PASS=... python -m fhir.seed   (from app/api)
"""
import pathlib
import random

from . import mapping as m
from .client import FhirClient
from rules.risk import Inputs, pce

NAMES = [  # made-up (family, given, gender)
    ("สุขสวัสดิ์", "สมชาย", "male"), ("ใจดี", "สมหญิง", "female"), ("แก้วมณี", "ประเสริฐ", "male"),
    ("รุ่งเรือง", "วิไล", "female"), ("ศรีสุวรรณ", "อนุชา", "male"), ("บุญมี", "สุนิสา", "female"),
    ("พรหมวงศ์", "ธนากร", "male"), ("วงศ์ใหญ่", "กัญญา", "female"), ("ทองคำ", "สมศักดิ์", "male"),
    ("จันทร์เพ็ญ", "นงลักษณ์", "female"), ("เจริญสุข", "ปรีชา", "male"), ("มั่นคง", "พิมพ์ใจ", "female"),
    ("สายทอง", "วิชัย", "male"), ("อินทร์แก้ว", "รัตนา", "female"), ("ขวัญเมือง", "บุญเลิศ", "male"),
    ("พิทักษ์", "ศิริพร", "female"), ("เพชรรัตน์", "อำนาจ", "male"), ("ดวงดี", "จันทนา", "female"),
    ("สมบูรณ์", "ชัยวัฒน์", "male"), ("นาคสุข", "อรทัย", "female"),
]
SEED_YEAR = 2026
PRIOR = {0, 7, 14}  # patients with a prior signed screening (all aged 40+ so PCE applies)


def _profile(i, rnd):
    """Deterministic age (30-79) and risk tier cycling low/mid/high."""
    age = 30 + (i * 7 + 3) % 50
    if i in PRIOR:
        age = max(age, 45)
    tier = i % 3
    return age, dict(
        sbp=[118, 136, 158][tier] + rnd.randint(-4, 4), dbp=[76, 86, 98][tier] + rnd.randint(-3, 3),
        tc=[170, 210, 260][tier] + rnd.randint(-8, 8), hdl=[60, 48, 36][tier] + rnd.randint(-3, 3),
        ldl=[100, 135, 175][tier] + rnd.randint(-8, 8), smoking=["never", "former", "current"][tier])


def _cond(entries, key, resource, fullurl=None):
    resource["identifier"] = [{"system": m.SEED_SYSTEM, "value": key}]
    entries.append(m.entry(fullurl or m.urn(), resource, f"identifier={m.SEED_SYSTEM}|{key}"))


def run(fhir=None):
    fhir = fhir or FhirClient(timeout=60)
    rnd = random.Random(20261017)
    common = []
    prac, dev = m.urn(), m.urn()
    _cond(common, "practitioner-gp", m.practitioner("seed-gp", "ผู้ช่วย", "หมอ"), prac)
    d = m.device("seed-prior-model", "seed-1", "2026-01-01")
    _cond(common, "device-seed", d, dev)
    fhir.transaction(common)
    prac_ref = f"Practitioner/{fhir.search('Practitioner', identifier=f'{m.SEED_SYSTEM}|practitioner-gp')[0]['id']}"
    dev_ref = f"Device/{fhir.search('Device', identifier=f'{m.SEED_SYSTEM}|device-seed')[0]['id']}"

    for i, (family, given, gender) in enumerate(NAMES):
        hn = f"HN-{i + 1:04d}"
        age, v = _profile(i, rnd)
        es, p = [], m.urn()
        pat = m.patient(hn, family, given, gender, f"{SEED_YEAR - age}-06-15", seed=True)
        es.append(m.entry(p, pat, f"identifier={m.MRN}|{hn}"))
        enc = m.urn()
        e = m.encounter(p, "screening", prac_ref)
        e["period"]["start"] = "2026-09-01T09:00:00+07:00"
        _cond(es, f"{hn}-enc-vitals", e, enc)
        for k, val in v.items():
            o = m.observation(k, val, p, enc)
            o["effectiveDateTime"] = "2026-09-01T09:00:00+07:00"
            _cond(es, f"{hn}-{k}", o)
        if i in PRIOR:  # prior signed screening: its own Encounter, a RiskAssessment and a final report
            penc = m.urn()
            pe = m.encounter(p, "screening", prac_ref)
            pe["period"]["start"] = "2026-03-10T10:00:00+07:00"
            _cond(es, f"{hn}-enc-prior", pe, penc)
            risk = pce(Inputs(age=age, sex=gender, sbp=v["sbp"], tc=v["tc"], hdl=v["hdl"], smoker=v["smoking"] == "current")).risk
            _cond(es, f"{hn}-prior-risk", m.risk_assessment(p, penc, "PCE (white)", risk, dev_ref))
            r = m.diagnostic_report(p, penc, "final", f"Prior screening: PCE 10-year risk {risk:.1f}%", [], [], prac_ref)
            r["issued"] = "2026-03-10T10:30:00+07:00"
            _cond(es, f"{hn}-prior-report", r)
        fhir.transaction(es)


def bootstrap(fhir, key_file):
    """Hosted start-up (live-demo-deployment D6): the store restarts empty. Raises until FHIR /metadata answers;
    then, if the seed patients are missing, drops the old store's image keys and withdrawal markers and seeds."""
    fhir.health_check()
    if len(fhir.search("Patient", identifier=f"{m.SEED_SYSTEM}|")) < len(NAMES):
        pathlib.Path(key_file).unlink(missing_ok=True)
        run(fhir)


if __name__ == "__main__":
    run()
    print("seeded")
