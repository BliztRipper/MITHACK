# Proposal

## Why

Cardiovascular disease kills about 80,000 Thais a year. Many high-risk people are never assessed because a full risk work-up needs labs and a clinician's time. On the acute side, central retinal artery occlusion (CRAO, an "eye stroke") is missed by non-ophthalmologists in the hours when stroke work-up matters most. Thailand already photographs the retina at scale: community hospitals run diabetic-retinopathy screening cameras. Those same photos can feed a CVD risk read and an emergency CRAO check for frontline GPs, without new hardware.

The team has a working CRAO triage prototype (`experiments/crao-prototype/`: quality gate, preprocessing, rule-based triage, training script, Gradio UI). It has no visual evidence (heatmap or segmentation), no calibrated confidence, no CVD risk, no persistence, no privacy controls and no feedback loop. All of these are needed for the hackathon demo and the trust story judges will test: EU AI Act, NIST AI RMF, Thai PDPA, and what happens when the model is wrong.

## What Changes

- New clinician web app (FastAPI backend + React frontend) with **one shared capture flow and two modes**:
  - **Screening mode:** fundus photo + clinical risk factors → 10-year CVD risk from the **Thai CV Risk Score** (headline, locally validated) and **ACC/AHA Pooled Cohort Equations** (shown alongside so the ACC/AHA 5 / 7.5 / 20% statin thresholds apply). **Retinal vascular markers** (artery/vein calibre, artery-to-vein ratio) act as *risk enhancers*, not as the risk number.
  - **Emergency mode:** fundus photo + onset time + symptoms → CRAO probability → deterministic triage card (the existing `triage.py` rules, migrated).
- **Visual evidence on every read:** vessel / artery-vein / optic-disc segmentation overlay, plus a model-attention heatmap in emergency mode, with opacity controls and a side-by-side view.
- **Calibrated confidence with a plain-language explanation:** temperature-scaled probability, a three-band display (unlikely / uncertain / likely), an abstain band, and a templated explanation naming the anatomical region the heatmap focused on and the known limitations. No LLM makes or words a clinical decision.
- **Image quality gate** before any model read, with a reason to retake.
- **Human oversight:** every AI result is *preliminary* until a clinician confirms or overrides it. Overrides are captured as labelled feedback.
- **InterSystems IRIS for Health FHIR R4 server as the system of record**, which replaces a separate mock database. It holds synthetic Thai patients, Consent, Media (images), Observations, RiskAssessment, DiagnosticReport, Device (model version), Provenance and AuditEvent.
- **Data protection for biometric retinal images (PDPA s.26):** explicit consent before capture, EXIF stripping, role-based access, an audit trail for every read, and image erasure on consent withdrawal.
- **Monitoring dashboard:** quality-reject rate, abstain rate, clinician agreement, calibration on reviewed cases, and drift alerts. The deployed model is locked: retraining happens offline, then the model is versioned and re-validated.
- Governance documents: model card, risk register mapped to NIST AI RMF and the EU AI Act high-risk obligations, and an intended-use statement.
- The prototype at `experiments/crao-prototype/` is superseded. Its `triage.py`, `vision.py` and `train.py` move into the new app with their self-checks kept as tests, and the old copy is removed after a parity check.

## Capabilities

### New Capabilities
- `retinal-image-intake`: consented capture of a fundus photo with mode selection, EXIF stripping and the image quality gate (accept / retake with reason).
- `retinal-image-analysis`: model inference over an accepted image. Produces segmentation overlays, an attention heatmap, a calibrated probability with confidence band and abstain, and a region-based explanation.
- `cvd-risk-assessment`: 10-year CVD risk from Thai CV Risk Score and PCE with input-range validation, retinal risk enhancers, clinical-factor prompts (such as arcus senilis), and guideline-based management suggestions.
- `crao-emergency-triage`: deterministic rules that turn CRAO probability, image quality, onset time and red-flag symptoms into a triage level and an ordered action list.
- `clinician-review`: preliminary results, clinician confirm/override with reason, sign-off into a final report, and the review queue.
- `fhir-clinical-records`: persistence and retrieval of patients, consent, images, inputs, AI outputs and reports as FHIR R4 resources on IRIS for Health, plus seeded synthetic Thai patients.
- `patient-data-protection`: authentication, role-based access, audit events, consent withdrawal and erasure, and handling of biometric images.
- `model-monitoring`: operational and performance metrics from reviewed cases, drift alerts, model version tracking, and export of reviewed cases for offline retraining.

### Modified Capabilities
<!-- None: no specs exist yet in openspec/specs/. -->

## Impact

- **New code:** `app/api` (FastAPI, PyTorch, timm), `app/web` (React + Vite + TypeScript), `app/fhir` (IRIS for Health Docker setup adapted from the InterSystems FHIR-AI-Hackathon-Kit, plus a seed script), `app/ml` (training and calibration), `docs/` (model card, risk register), and `docker-compose.yml`.
- **Moved / removed:** `experiments/crao-prototype/` is migrated into `app/` and then deleted.
- **Dependencies:** FastAPI, uvicorn, torch, timm, opencv, numpy, httpx (FHIR client), AutoMorph (Apache-2.0, vessel / artery-vein / disc segmentation), RETFound weights (CC BY-NC 4.0, gated on Hugging Face, **research/demo only**), React, Vite, Tailwind, and Playwright (already a devDependency) for one end-to-end smoke test.
- **Infrastructure:** Docker running `intersystemsdc/irishealth-community`, with FHIR at `http://localhost:32783/csp/healthshare/demo/fhir/r4`.
- **Data:** Mendeley RAO fundus v2 (CC BY 4.0, about 151 images) and RFMiD 1.0 (CC BY 4.0) for the CRAO head. No public data links fundus photos to CVD outcomes, so the retinal contribution to CVD is limited to literature-backed vascular markers used as enhancers.
- **Business/licensing:** RETFound is non-commercial, so a commercial product needs a licence or a swap to an Apache-2.0 backbone (FLAIR). The demo states this.
- **Not in scope:** real patient data, a production deployment, online learning, an LLM chatbot, OCT input, and claims of hyperacute (<4.5 h) CRAO accuracy, since no public hyperacute images exist.
