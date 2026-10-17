"""Consent withdrawal (PDPA erasure, design D9): delete images, destroy the data key, keep report text."""
from . import mapping as m


def withdraw(fhir, keys, patient_id, user, role):
    pref = f"Patient/{patient_id}"
    for med in fhir.search("Media", subject=pref):
        fhir.delete("Media", med["id"])
    keys.destroy(patient_id)  # FHIR keeps history on delete; without the key those copies are noise
    for rep in fhir.search("DiagnosticReport", subject=pref):
        if "media" in rep:  # signed report text stays, image references go
            del rep["media"]
            fhir.update(rep)
    for c in fhir.search("Consent", patient=pref):
        if c["status"] != "inactive":
            c["status"] = "inactive"
            fhir.update(c)
    fhir.create(m.audit_event(user, role, "D", pref))  # records the withdrawal
