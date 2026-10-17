"""Consent withdrawal (PDPA erasure, design D9): delete images, destroy the data key, keep report text."""
import contextlib

from . import mapping as m


def _key_ids(media):
    return [e["valueString"] for x in media.get("extension", []) for e in x.get("extension", []) if e["url"] == "keyId"]


def withdraw(fhir, keys, patient_id, user, role):
    patient_id = patient_id.rsplit("/", 1)[-1]
    pref = f"Patient/{patient_id}"
    try:
        # Consent first: if anything below fails, exports and new uploads are already blocked.
        for c in fhir.search("Consent", patient=pref):
            if c["status"] != "inactive":
                c["status"] = "inactive"
                fhir.update(c)
        media = fhir.search("Media", subject=pref)
        keys.destroy(patient_id)  # FHIR keeps history on delete; without the key those copies are noise
        for med in media:
            fhir.delete("Media", med["id"])
            for kid in _key_ids(med):
                if keys.has_key(patient_id, kid):
                    raise RuntimeError(f"key {kid} still present after destroy for {pref}")
        for rep in fhir.search("DiagnosticReport", subject=pref):
            if "media" in rep:  # report text stays and keeps its status (not "amended": no clinical content changed)
                del rep["media"]
                fhir.update(rep)
    except Exception:
        with contextlib.suppress(Exception):
            fhir.create(m.audit_event(user, role, "D", pref, outcome="8"))
        raise
    fhir.create(m.audit_event(user, role, "D", pref))  # records the withdrawal
