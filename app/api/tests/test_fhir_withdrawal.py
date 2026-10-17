import base64
import os

import pytest

from fhir import mapping as m
from fhir.client import FhirError
from fhir.crypto import ConsentWithdrawn, KeyDestroyed, KeyStore
from fhir.withdrawal import withdraw

pytestmark = pytest.mark.fhir


class World:
    def __init__(self, fhir, ks, hn):
        self.fhir, self.ks, self.made = fhir, ks, []
        self.pid = self.mk(m.patient(hn, "Testwd", "W", "male", "1975-05-05"))
        self.P = f"Patient/{self.pid}"
        self.prac = f"Practitioner/{self.mk(m.practitioner('test-wd', 'Testprac', 'W'))}"
        self.enc = f"Encounter/{self.mk(m.encounter(self.P, 'screening', self.prac))}"
        self.cons = [self.mk(m.consent(self.P, "care")), self.mk(m.consent(self.P, "model-improvement"))]

    def mk(self, r):
        out = self.fhir.create(r)
        self.made.append((r["resourceType"], out["id"]))
        return out["id"]

    def image(self, pid_form=None, img=b"fake-image-bytes" * 50):
        blob, kid = self.ks.encrypt(pid_form or self.pid, img)
        med = self.mk(m.media(self.P, self.enc, blob, kid))
        rep = self.mk(m.diagnostic_report(self.P, self.enc, "final", "Moderate risk, see GP", [], [f"Media/{med}"], self.prac))
        return blob, kid, med, rep

    def audits(self, outcome=None):
        return [a for a in self.fhir.search("AuditEvent", entity=self.P, action="D") if outcome in (None, a["outcome"])]

    def cleanup(self):
        for a in self.fhir.search("AuditEvent", entity=self.P):
            self.fhir.delete("AuditEvent", a["id"])
        for t, i in reversed(self.made):
            if t != "Media":
                self.fhir.delete(t, i)


@pytest.fixture
def world(fhir, tmp_path, request):
    w = World(fhir, KeyStore(os.urandom(32), tmp_path / "keys.json"), "TEST-WD-" + request.node.name[:12])
    yield w
    w.cleanup()


def _history_undecryptable(w, med, kid):
    versions = [v for v in w.fhir.history("Media", med) if "content" in v]
    assert versions, "expected history to retain the encrypted Media"
    for v in versions:
        with pytest.raises(KeyDestroyed):
            w.ks.decrypt(w.pid, base64.b64decode(v["content"]["data"]), kid)


def test_withdrawal_erases_images_keeps_report_text(world):
    w, fhir = world, world.fhir
    blob, kid, med, rep_id = w.image()
    withdraw(fhir, w.ks, w.pid, "test-gp", "clinician")
    with pytest.raises(FhirError) as e:
        fhir.read("Media", med)
    assert e.value.status == 410
    assert fhir.search("Media", subject=w.P) == []
    rep = fhir.read("DiagnosticReport", rep_id)
    assert rep["conclusion"] == "Moderate risk, see GP" and rep["status"] == "final" and "media" not in rep
    assert all(fhir.read("Consent", c)["status"] == "inactive" for c in w.cons)
    assert w.audits("0")
    _history_undecryptable(w, med, kid)  # IRIS keeps history: ciphertext there, key gone
    with pytest.raises(KeyDestroyed):
        w.ks.decrypt(w.pid, blob, kid)
    with pytest.raises(ConsentWithdrawn):  # next upload cannot silently create a new key
        w.ks.encrypt(w.pid, b"again")


def test_id_form_mismatch_still_erases(world):
    w = world
    _, kid, med, _ = w.image(pid_form=w.P)  # encrypted under "Patient/<id>" like case_bundle callers
    withdraw(w.fhir, w.ks, w.pid, "test-gp", "clinician")  # withdrawn under the bare id
    _history_undecryptable(w, med, kid)


def test_withdraw_twice_and_without_key(world):
    w = world
    withdraw(w.fhir, w.ks, w.pid, "test-gp", "clinician")  # no key, no media
    withdraw(w.fhir, w.ks, w.pid, "test-gp", "clinician")
    assert len(w.audits("0")) == 2 and not w.audits("8")


def test_failure_midway_leaves_consent_inactive_and_audits(world, monkeypatch):
    w = world
    w.image()
    def boom(*a, **k):
        raise FhirError(500, "error:exception")
    monkeypatch.setattr(w.fhir, "delete", boom)
    with pytest.raises(FhirError):
        withdraw(w.fhir, w.ks, w.pid, "test-gp", "clinician")
    monkeypatch.undo()
    assert all(w.fhir.read("Consent", c)["status"] == "inactive" for c in w.cons)
    assert len(w.audits("8")) == 1
    withdraw(w.fhir, w.ks, w.pid, "test-gp", "clinician")  # retry finishes the job
    assert w.fhir.search("Media", subject=w.P) == []
