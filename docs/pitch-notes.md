# Pitch notes

Every claim carries a source: a spec (`spec <capability>: <Requirement>`), a design decision (`design Dn`), the proposal, or `docs/`. Anything without a source was cut.

## The problem
- Many high-risk people are never assessed, because a full work-up needs labs and clinician time. CRAO is missed by non-ophthalmologists when stroke work-up matters most (proposal, Why).
- Thailand already photographs the retina at scale in community-hospital diabetic-retinopathy screening, so no new hardware is needed (proposal, Why).

## User flow (corrected)
Consent and clinical inputs come first and a clinician signs between AI output and action (design, Context):
patient → mode → PDPA consent → inputs → fundus upload → EXIF strip → quality gate → segmentation → Screening (PCE → statin group → enhancers) or Emergency (CRAO band + heatmap → triage rules) → templated explanation → **preliminary** → clinician confirm/override → final report and TH/EN patient summary → monitoring.

## Why retinal markers are risk enhancers, not the risk number
- No public data links fundus photos to CVD outcomes, so the risk number comes from the 2013 ACC/AHA Pooled Cohort Equations and the retina only adds literature-backed vascular markers (proposal, Impact; design D7).
- Retinal enhancers are labelled investigational, not guideline-listed, and never change the calculated number (spec cvd-risk-assessment: Risk enhancers).
- AVR is the primary marker because it is unitless. CRAE/CRVE need a camera-dependent pixel scale, so they are shown but not flagged (design D5).
- The AVR reference interval is a literature placeholder, labelled so, and an open question (design Open Questions).

## Risk model: PCE, caveat, PREVENT
- Screening uses the 2013 ACC/AHA PCE, ages 40–79, with ACC/AHA bands and 2018 AHA/ACC statin groups (spec cvd-risk-assessment: Pooled Cohort Equations, Risk categories and management suggestions, Calculator bypass for statin benefit groups).
- **Asian-population caveat, shown on every result:** PCE was not derived in Asian populations and may overestimate risk (spec cvd-risk-assessment: Pooled Cohort Equations; design Risks).
- **AHA PREVENT (2023) was considered and rejected** for demo scope. PCE is built and tested against the published worked examples, while PREVENT needs eGFR and BMI inputs and new equations (design D7). It is the natural next step.
- Coefficients are not yet checked against the published paper (design Risks); say so if asked.

## Data ceiling (state it before a judge asks)
- The CRAO head would train on about 151 public established-RAO images (Mendeley RAO v2, CC BY 4.0) plus RFMiD 1.0, also CC BY 4.0 (proposal, Impact; design Non-Goals).
- **No trained CRAO model exists in this build.** The demo runs "no model loaded", so Emergency cases are ESCALATE (spec retinal-image-analysis: Degraded operation without model weights; `docs/intended-use.md`).
- No claim of hyperacute (<4.5 h) accuracy: no public hyperacute images exist (proposal, Not in scope).
- Thresholds are placeholders, not clinically validated (spec crao-emergency-triage: Configurable thresholds).

## Trust story
- A normal-looking photo does not reassure (spec crao-emergency-triage: Normal-looking photo does not reassure).
- Triage is deterministic, readable rules with reasons. No LLM touches a decision or an explanation (design Goals; spec crao-emergency-triage: Reasons shown with every level).
- Heatmap says "model attention, not confirmed lesions" (spec retinal-image-analysis: Attention heatmap in Emergency mode).
- Monitoring flags near-100% agreement as rubber-stamping (spec model-monitoring: Drift alerts).
- Hazards and residual risk, mapped to NIST AI RMF and the EU AI Act: `docs/risk-register.md`.

## InterSystems IRIS for Health
- IRIS for Health is the **FHIR R4 clinical data repository** and the only clinical store. No second database (spec fhir-clinical-records: FHIR server is the system of record; design D8).
- Each case save is one **transaction Bundle**, all or nothing. Seeding uses **conditional create**, so re-running it adds no duplicates (design D8; spec fhir-clinical-records: Synthetic Thai demo patients).
- **Version history underpins crypto-shredding.** FHIR keeps history on delete, so images are encrypted per patient and the patient key is destroyed on consent withdrawal. History copies then cannot be decrypted (design D9; spec patient-data-protection: Consent withdrawal and erasure).
- **14 resource types** in use: Patient, Consent, Encounter, Media, Observation, Condition, RiskAssessment, DiagnosticReport, Device, Provenance, AuditEvent, Practitioner, Flag and Organization (spec fhir-clinical-records: Resource mapping; design D8). The code adds Practitioner and Flag (design D8) and Organization (the Flag subject, since R4 does not allow a Device subject) beyond the spec's list of 11 (`app/api/fhir/mapping.py`).
- Starting point: the InterSystems FHIR-AI-Hackathon-Kit (MIT, attributed), IRIS for Health Community in Docker with FHIR R4 (design Context, D1).

## PDPA biometric handling
Retinal images are biometric and health data under PDPA s.26 (proposal, What Changes; spec retinal-image-intake: Consent gate for biometric capture). Controls: explicit purpose-limited consent (spec patient-data-protection: Purpose-limited consent), EXIF/GPS stripping (spec retinal-image-intake: Metadata stripping), encryption (spec patient-data-protection: Encryption of retinal images), audit of every access (spec patient-data-protection: Access audit trail), erasure on withdrawal with the signed report text kept. Whether the law requires keeping that report is a legal-check item (design Open Questions).

## Licensing and the RETFound swap
- RETFound weights are CC BY-NC 4.0, gated on Hugging Face: demo and research only (design Context, D2; proposal, Impact).
- Commercial use needs a licence or a swap to FLAIR (Apache-2.0). The swap is documented, not built (design D2).
- EfficientNet-B0 is the fallback if access is not granted, with no code impact (design D2). Access has not been requested yet (`docs/model-card.md`).

## Business model and regulatory path (hypothesis only)
- Channel: existing diabetic-retinopathy screening sites and hospitals (proposal, Why). The pricing form (per-screen fee or hospital SaaS) is a team hypothesis. No price, market-size or revenue figure is claimed, because none is sourced.
- Regulatory: this is not a cleared medical device (`docs/intended-use.md`). The Thai FDA software-as-a-medical-device route has not been assessed in the plan and is not claimed here. The EU AI Act self-assessment is in `docs/risk-register.md`.

## Known limits to volunteer
- Demo cache covers 4 of 6 curated images; an uncached live analysis can exceed 90 s (design D11; task reports). AutoMorph's full pipeline took 33–61 s cold (`docs/model-card.md`).
- AutoMorph's AVR on the gradable demo images (0.55–0.59) falls below the placeholder interval, so the retinal enhancer flags them (`app/api/demo_cache/*/meta.json`: 0.548, 0.550, 0.588).
- An IRIS superuser can edit records, and the audit log is not tamper-evident (design D10).
