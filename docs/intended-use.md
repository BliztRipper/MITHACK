# Intended use

Hackathon prototype (Siriraj x MIT, Cardiovascular track). **Not a medical device. Not validated. Not for patient care.** It runs on synthetic Thai patients only.

## Intended users
Frontline clinicians who are not ophthalmologists (GPs, emergency doctors, nurses at diabetic-retinopathy screening sites), plus ophthalmologist reviewers and administrators. Roles: spec patient-data-protection: Role-based permissions.

## Intended use
Clinical **decision support** from a colour fundus photograph and clinician-entered data. A clinician reads and signs every result (spec clinician-review: AI results are preliminary until signed).

| Mode | Output | Basis |
|---|---|---|
| Screening | 10-year ASCVD risk, ACC/AHA band, 2018 AHA/ACC statin benefit group, investigational retinal-vessel enhancers | 2013 ACC/AHA Pooled Cohort Equations (design D7); spec cvd-risk-assessment |
| Emergency | CRAO probability band, attention heatmap, deterministic triage card | spec crao-emergency-triage, spec retinal-image-analysis |

## Not intended for
- Diagnosis, or replacing clinician judgement. The result is preliminary and labelled "AI-assisted, not a diagnosis".
- Ruling CRAO out. A normal-looking photo does not reassure: sudden painless one-eye vision loss within 24 h or of unknown onset is escalated (spec crao-emergency-triage: Normal-looking photo does not reassure).
- Hyperacute (<4.5 h) CRAO accuracy. The model, once trained, sees established occlusions only (proposal, Not in scope).
- Predicting CVD events from the retina. No outcome-linked fundus data exists (proposal, Impact). Retinal markers are investigational enhancers and never change the risk number (spec cvd-risk-assessment: Risk enhancers).
- Real patient data, production use, commercial use (RETFound is CC BY-NC 4.0; design D2).

## Contraindications and exclusions
- Age outside 40–79: no PCE number, "outside validated age range (40–79)" (spec cvd-risk-assessment: Pooled Cohort Equations).
- Known ASCVD, LDL ≥190 mg/dL, or diabetes at 40–75 with LDL ≥70: calculators do not set treatment (spec cvd-risk-assessment: Calculator bypass for statin benefit groups).
- Inputs outside range (e.g. SBP 400): rejected, never clamped (design D7).
- Image failing the quality gate or not a fundus photograph: no analysis, retake (spec retinal-image-intake: Image quality gate).
- No active consent for retinal image processing: no upload (spec retinal-image-intake: Consent gate for biometric capture).
- Suspected giant cell arteritis: arteritis action first, no stroke-team card (spec crao-emergency-triage: Giant cell arteritis branch).
- PCE was not derived in Asian populations and may overestimate risk. AHA PREVENT was considered and rejected for demo scope (design D7).

## Known limits of this build
- No trained CRAO model: no negative training data. The demo runs "no model loaded", so Emergency cases are ESCALATE (spec retinal-image-analysis: Degraded operation without model weights).
- Triage and band thresholds, the AVR reference interval and the quality threshold are placeholders, not clinically validated (spec crao-emergency-triage: Configurable thresholds).
- PCE coefficients are not yet checked against the published paper (design Risks).
- Demo cache covers 4 of 6 curated images; an uncached live analysis can exceed 90 s.
