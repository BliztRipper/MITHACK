"""Builders for the FHIR R4 resources the platform stores (spec: fhir-clinical-records). Plain dicts.

Builders reference each other with strings ("Patient/1" or "urn:uuid:..." inside a transaction).
Codes marked LOCAL are not LOINC: the spec lists LOINC only for vitals/labs/smoking.
"""
import base64
import uuid
from datetime import datetime, timezone

LOINC = "http://loinc.org"
LOCAL = "https://retina-platform.example/CodeSystem/local"  # LOCAL codes: no LOINC given in spec
MRN = "https://retina-platform.example/hospital-number"
ENC_EXT = "https://retina-platform.example/StructureDefinition/image-encryption"
SEED_SYSTEM = "https://retina-platform.example/synthetic-seed"

# spec-listed LOINC codes
OBS_CODES = {
    "sbp": (LOINC, "8480-6", "Systolic blood pressure"),
    "dbp": (LOINC, "8462-4", "Diastolic blood pressure"),
    "tc": (LOINC, "2093-3", "Total cholesterol"),
    "hdl": (LOINC, "2085-9", "HDL cholesterol"),
    "ldl": (LOINC, "18262-6", "LDL cholesterol"),
    "smoking": (LOINC, "72166-2", "Tobacco smoking status"),
    # LOCAL
    "arcus_senilis": (LOCAL, "arcus-senilis", "Arcus senilis"),
    "crao_probability": (LOCAL, "crao-probability", "CRAO probability (AI)"),
    "quality_score": (LOCAL, "image-quality-score", "Image quality score"),
    "waist": (LOCAL, "waist-circumference", "Waist circumference"),
    "height": (LOCAL, "height", "Height"),
    "vessel_avr": (LOCAL, "vessel-avr", "Arteriole-venule ratio"),
    "vessel_tortuosity": (LOCAL, "vessel-tortuosity", "Vessel tortuosity"),
}
UNITS = {"sbp": "mm[Hg]", "dbp": "mm[Hg]", "tc": "mg/dL", "hdl": "mg/dL", "ldl": "mg/dL", "waist": "cm", "height": "cm"}


def urn():
    return f"urn:uuid:{uuid.uuid4()}"


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ref(x):
    return {"reference": x}


def patient(hn, family, given, gender, birth_date, seed=False):
    ids = [{"system": MRN, "value": hn}]
    if seed:
        ids.append({"system": SEED_SYSTEM, "value": hn})
    return {"resourceType": "Patient", "identifier": ids, "name": [{"family": family, "given": [given]}],
            "gender": gender, "birthDate": birth_date}


def practitioner(username, family, given):
    return {"resourceType": "Practitioner", "identifier": [{"system": f"{LOCAL}/user", "value": username}],
            "name": [{"family": family, "given": [given]}]}


def consent(patient_ref, purpose, active=True):
    """One Consent per purpose: 'care' (required) or 'model-improvement' (optional)."""
    return {"resourceType": "Consent", "status": "active" if active else "inactive",
            "scope": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/consentscope", "code": "patient-privacy"}]},
            "category": [{"coding": [{"system": LOINC, "code": "59284-0"}]}],
            "patient": ref(patient_ref), "dateTime": now(),
            "provision": {"type": "permit", "purpose": [{"system": LOCAL, "code": purpose}]}}


def device(name, version, calibration_date):
    return {"resourceType": "Device", "status": "active", "deviceName": [{"name": name, "type": "model-name"}],
            "version": [{"value": version}],
            "property": [{"type": {"text": "calibration-date"}, "valueCode": [{"text": calibration_date}]}]}


def encounter(patient_ref, mode, practitioner_ref):
    return {"resourceType": "Encounter", "status": "finished",
            "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "AMB"},
            "type": [{"coding": [{"system": LOCAL, "code": mode}]}],  # screening | emergency
            "subject": ref(patient_ref), "participant": [{"individual": ref(practitioner_ref)}],
            "period": {"start": now()}}


def media(patient_ref, encounter_ref, ciphertext, key_id, kind="fundus", alg="AES-256-GCM"):
    """ciphertext is already encrypted (see fhir/crypto.py); the image never reaches FHIR in clear."""
    return {"resourceType": "Media", "status": "completed",
            "type": {"coding": [{"system": LOCAL, "code": kind}]},  # fundus | overlay
            "subject": ref(patient_ref), "encounter": ref(encounter_ref),
            "extension": [{"url": ENC_EXT, "extension": [
                {"url": "algorithm", "valueString": alg}, {"url": "keyId", "valueString": key_id}]}],
            "content": {"contentType": "application/octet-stream", "data": base64.b64encode(ciphertext).decode()}}


def observation(key, value, patient_ref, encounter_ref, device_ref=None):
    system, code, text = OBS_CODES[key]
    o = {"resourceType": "Observation", "status": "final", "code": {"coding": [{"system": system, "code": code, "display": text}]},
         "subject": ref(patient_ref), "encounter": ref(encounter_ref), "effectiveDateTime": now()}
    if isinstance(value, bool):
        o["valueBoolean"] = value
    elif isinstance(value, str):
        o["valueCodeableConcept"] = {"text": value}
    else:
        o["valueQuantity"] = {"value": value, **({"unit": UNITS[key]} if key in UNITS else {})}
    if device_ref:  # AI-produced outputs name their model version
        o["device"] = ref(device_ref)
    return o


def condition(patient_ref, text, code):
    return {"resourceType": "Condition", "subject": ref(patient_ref),
            "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]},
            "code": {"coding": [{"system": LOCAL, "code": code}], "text": text}}


def risk_assessment(patient_ref, encounter_ref, method, risk_pct, device_ref):
    """method names the equation, e.g. 'Thai CV Risk (lab)' or 'PCE (white)'."""
    return {"resourceType": "RiskAssessment", "status": "final", "method": {"text": method},
            "subject": ref(patient_ref), "encounter": ref(encounter_ref), "performer": ref(device_ref),
            "prediction": [{"outcome": {"text": "10-year CVD risk"}, "probabilityDecimal": risk_pct, "whenRange": {"high": {"value": 10, "unit": "years"}}}]}


def diagnostic_report(patient_ref, encounter_ref, status, conclusion, result_refs, media_refs, performer_ref):
    """status: preliminary | final | amended."""
    r = {"resourceType": "DiagnosticReport", "status": status, "code": {"coding": [{"system": LOCAL, "code": "retinal-ai-report"}]},
         "subject": ref(patient_ref), "encounter": ref(encounter_ref), "issued": now(), "performer": [ref(performer_ref)],
         "conclusion": conclusion}
    if result_refs:  # IRIS rejects empty arrays
        r["result"] = [ref(x) for x in result_refs]
    if media_refs:
        r["media"] = [{"link": ref(x)} for x in media_refs]
    return r


def provenance(target_refs, agent_ref, agent_type):
    """agent_type: 'device' (AI) or 'author' (signing clinician)."""
    return {"resourceType": "Provenance", "target": [ref(t) for t in target_refs], "recorded": now(),
            "agent": [{"type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
                                            "code": "author" if agent_type == "author" else "assembler"}]},
                       "who": ref(agent_ref)}]}


def audit_event(user, role, action, entity_ref, outcome="0"):
    """action: C|R|U|D|E. outcome '0' success, '4' minor failure, '8' serious failure."""
    return {"resourceType": "AuditEvent", "type": {"system": "http://dicom.nema.org/resources/ontology/DCM", "code": "110110"},
            "action": action, "recorded": now(), "outcome": outcome,
            "agent": [{"who": {"display": user}, "role": [{"text": role}], "requestor": True}],
            "source": {"observer": {"display": "retina-platform-api"}},
            "entity": [{"what": ref(entity_ref)}]}


def flag(org_ref, device_ref, category, text):
    """category: 'drift' | 'ai-incident'. R4 Flag.subject cannot be a Device, so the site Organization is the
    subject and the Device is carried in an extension."""
    return {"resourceType": "Flag", "status": "active", "category": [{"coding": [{"system": LOCAL, "code": category}]}],
            "code": {"text": text}, "subject": ref(org_ref),
            "extension": [{"url": f"{LOCAL}/device", "valueReference": ref(device_ref)}]}


def entry(fullurl, resource, if_none_exist=None):
    req = {"method": "POST", "url": resource["resourceType"]}
    if if_none_exist:
        req["ifNoneExist"] = if_none_exist
    return {"fullUrl": fullurl, "resource": resource, "request": req}


def case_bundle(mode, patient_ref, practitioner_ref, device_ref, ciphertexts, obs, risks=(), conditions=(),
                status="final", conclusion=""):
    """One all-or-nothing transaction for a case.

    mode: 'screening' | 'emergency'. ciphertexts: [(kind, bytes, key_id)]. obs: {key: value}; keys in
    AI_KEYS are written with the Device ref. risks: [(method, pct)]. Returns (entries, report_urn).
    """
    ai_keys = {"crao_probability", "quality_score", "vessel_avr", "vessel_tortuosity"}
    enc = urn()
    es = [entry(enc, encounter(patient_ref, mode, practitioner_ref))]
    media_urns = []
    for kind, data, key_id in ciphertexts:
        u = urn(); media_urns.append(u)
        es.append(entry(u, media(patient_ref, enc, data, key_id, kind)))
    results = []
    for k, v in obs.items():
        u = urn(); results.append(u)
        es.append(entry(u, observation(k, v, patient_ref, enc, device_ref if k in ai_keys else None)))
    for method, pct in risks:  # DiagnosticReport.result allows only Observation; Encounter links the rest
        es.append(entry(urn(), risk_assessment(patient_ref, enc, method, pct, device_ref)))
    for text, code in conditions:
        es.append(entry(urn(), condition(patient_ref, text, code)))
    rep = urn()
    es.append(entry(rep, diagnostic_report(patient_ref, enc, status, conclusion, results, media_urns, practitioner_ref)))
    es.append(entry(urn(), provenance([rep], practitioner_ref if status == "final" else device_ref,
                                      "author" if status == "final" else "device")))
    es.append(entry(urn(), audit_event(practitioner_ref, "clinician", "C", rep)))
    return es, rep
