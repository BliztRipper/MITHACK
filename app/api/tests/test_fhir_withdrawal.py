import base64
import os

import pytest

from fhir import mapping as m
from fhir.crypto import KeyDestroyed, KeyStore
from fhir.client import FhirError
from fhir.withdrawal import withdraw

pytestmark = pytest.mark.fhir


def test_withdrawal_erases_images_keeps_report_text(fhir, tmp_path):
    ks = KeyStore(os.urandom(32), tmp_path / "keys.json")
    made = []
    def mk(r):
        out = fhir.create(r); made.append((r["resourceType"], out["id"])); return out["id"]
    try:
        pid = mk(m.patient("TEST-WD", "Testwd", "W", "male", "1975-05-05"))
        P = f"Patient/{pid}"
        prac = f"Practitioner/{mk(m.practitioner('test-wd', 'Testprac', 'W'))}"
        enc = f"Encounter/{mk(m.encounter(P, 'screening', prac))}"
        cons = [mk(m.consent(P, "care")), mk(m.consent(P, "model-improvement"))]
        img = b"fake-image-bytes" * 50
        blob, kid = ks.encrypt(pid, img)
        med_id = mk(m.media(P, enc, blob, kid))
        rep_id = mk(m.diagnostic_report(P, enc, "final", "Moderate risk, see GP", [], [f"Media/{med_id}"], prac))
        assert ks.decrypt(pid, blob, kid) == img

        withdraw(fhir, ks, pid, "test-gp", "clinician")

        with pytest.raises(FhirError) as e:  # image can no longer be retrieved
            fhir.read("Media", med_id)
        assert e.value.status == 410
        assert fhir.search("Media", subject=P) == []
        rep = fhir.read("DiagnosticReport", rep_id)
        assert rep["conclusion"] == "Moderate risk, see GP" and rep["status"] == "final" and "media" not in rep
        assert all(fhir.read("Consent", c)["status"] == "inactive" for c in cons)
        assert fhir.search("AuditEvent", entity=P, action="D")
        # IRIS keeps history: prove the ciphertext is still there but undecryptable
        versions = [v for v in fhir.history("Media", med_id) if "content" in v]
        assert versions, "expected history to retain the encrypted Media"
        for v in versions:
            with pytest.raises(KeyDestroyed):
                ks.decrypt(pid, base64.b64decode(v["content"]["data"]), kid)
        with pytest.raises(KeyDestroyed):
            ks.decrypt(pid, blob, kid)
    finally:
        for t, i in reversed(made):
            if t != "Media":
                fhir.delete(t, i)
        for a in fhir.search("AuditEvent", entity=f"Patient/{pid}"):
            fhir.delete("AuditEvent", a["id"])
