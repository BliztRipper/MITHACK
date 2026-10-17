# Risk register

Scope: the retina CVD/CRAO decision-support prototype (see `intended-use.md`). Mitigations cite the spec as `spec <capability>: <Requirement title>`. Spec files: `openspec/changes/retina-cvd-crao-platform/specs/`.

Key. **NIST**: AI RMF 1.0 function (Govern, Map, Measure, Manage). **EU AI Act**: high-risk obligation (Art. 9 risk management, 10 data governance, 12 logging, 13 transparency, 14 human oversight, 15 accuracy/robustness/cybersecurity). Residual risk is rated after mitigation: low / medium / high.

## H1. Missed CRAO (false reassurance)
Early CRAO can look normal on a photo, and the model is trained on established occlusions only.
- Normal-looking photo with a fitting story is ESCALATE, not ROUTINE: `spec crao-emergency-triage: Normal-looking photo does not reassure`.
- "Uncertain" never reads as negative: `spec retinal-image-analysis: Calibrated probability with confidence band`.
- Limitation sentences on every Emergency explanation: `spec retinal-image-analysis: Region-based explanation`.
- No model loaded gives ESCALATE: `spec retinal-image-analysis: Degraded operation without model weights`.
- Late misses are reportable: `spec model-monitoring: Incident reporting`.

NIST: Map, Manage. EU AI Act: Art. 9, 13, 15. **Residual: high.** Thresholds are placeholders, not clinically validated, and no trained model exists yet. Sensitivity is unknown.

## H2. False CRAO (over-triage)
Unneeded stroke-team activation or referral; a mimic (CRVO, GCA) mistaken for CRAO.
- Output is a band with reasons, not a diagnosis: `spec crao-emergency-triage: Reasons shown with every level`.
- GCA gets its own first action and never the stroke-team card: `spec crao-emergency-triage: Giant cell arteritis branch`.
- Clinician confirms or overrides with a reason: `spec clinician-review: Confirm or override with reason`.
- Override rate is watched: `spec model-monitoring: Drift alerts`.

NIST: Map, Measure. EU AI Act: Art. 14, 15. **Residual: medium.** Specificity is unmeasured. Over-triage costs time, not harm, but stroke-pathway activation is resource-heavy.

## H3. Poor or wrong image
Dark, blurred, partial or non-fundus photo gives a meaningless output.
- Gate runs before any model and gives a retake reason: `spec retinal-image-intake: Image quality gate`.
- Gate failure overrides the model, with an urgent-referral fallback so retake never delays care: `spec crao-emergency-triage: Quality gate overrides the model`.
- Format and size limits: `spec retinal-image-intake: Accepted image formats and size`.
- Retinal enhancers skipped, and the report says so, when the image fails: `spec cvd-risk-assessment: Risk enhancers`.

NIST: Measure, Manage. EU AI Act: Art. 10, 15. **Residual: medium.** The gate is a hand-tuned heuristic (tuned on 12 camera photos, `app/api/vision/quality.py` lines 71-72). It rejects 16 of 127 web-crawled RAO figures (same source), and AutoMorph's quality grade may disagree with it.

## H4. Automation bias
A busy GP accepts every output; the heatmap is read as a lesion map.
- All results are preliminary until signed: `spec clinician-review: AI results are preliminary until signed`.
- Overrides need a reason and capture the label: `spec clinician-review: Confirm or override with reason`.
- Heatmap labelled "model attention, not confirmed lesions": `spec retinal-image-analysis: Attention heatmap in Emergency mode`.
- Agreement near 100% raises an alert: `spec model-monitoring: Drift alerts`.
- Reviewer sees ESCALATE cases: `spec clinician-review: Review queue`.

NIST: Govern, Manage. EU AI Act: Art. 14. **Residual: medium.** Sign-off is a click. The alert detects rubber-stamping only after the fact, over 50 cases.

## H5. Data breach or unlawful processing of biometric images
Retinal images are biometric and health data (Thai PDPA s.26).
- Login and 30-minute session expiry: `spec patient-data-protection: Authenticated access`.
- Three roles; admins cannot open images: `spec patient-data-protection: Role-based permissions`.
- Per-patient AES-256-GCM encryption, no images in logs: `spec patient-data-protection: Encryption of retinal images` (design D9).
- Explicit consent before capture, separate care and model-improvement purposes: `spec retinal-image-intake: Consent gate for biometric capture`, `spec patient-data-protection: Purpose-limited consent`.
- EXIF/GPS removed: `spec retinal-image-intake: Metadata stripping`.
- Withdrawal deletes images and destroys the patient key (crypto-shredding); the signed report text stays: `spec patient-data-protection: Consent withdrawal and erasure`.
- Every read and write is audited, append-only through the app: `spec patient-data-protection: Access audit trail`.
- The one clinical store is the FHIR server, bound to localhost: `spec fhir-clinical-records: FHIR server is the system of record`.
- Retraining export is de-identified and consented only: `spec model-monitoring: Reviewed-case export for retraining`.

NIST: Govern, Manage. EU AI Act: Art. 10, 12, 15. **Residual: medium (demo) / high (production).** Design D10 limitation: an IRIS superuser can edit or delete records and the audit log, and there is no tamper-evident log. Keys sit in a local file under a master key from an environment variable. There is no real identity provider, and demo users live in a YAML file. Whether Thai medical-record law requires keeping reports after withdrawal needs a legal check (design Open Questions).

## H6. Model drift and silent degradation
Camera mix, population or case mix changes; performance falls unnoticed.
- Dashboard of quality-reject, uncertain, agreement and override rates per model version: `spec model-monitoring: Monitoring dashboard`.
- Reliability on signed cases; "insufficient data" below 30 cases: `spec model-monitoring: Calibration on reviewed cases`.
- Rolling-window alerts: `spec model-monitoring: Drift alerts`.
- No learning at runtime; every result names its model version: `spec model-monitoring: Locked, versioned model`, `spec fhir-clinical-records: AI provenance on every output`.

NIST: Measure, Manage. EU AI Act: Art. 9, 12, 15. **Residual: medium.** Alert limits are placeholders. Ground truth is the clinician's label, which can be wrong. At demo volume, windows of 50 and calibration at 30 are rarely reached.

## H7. PCE miscalibration
PCE was not derived in Asian populations and may overestimate risk. Coefficients could be mistranscribed.
- Caveat on every result: `spec cvd-risk-assessment: Pooled Cohort Equations`.
- Out-of-age patients get no number; out-of-range inputs are rejected: `spec cvd-risk-assessment: Pooled Cohort Equations`, `spec cvd-risk-assessment: Risk factor inputs`.
- Statin-benefit patients are not driven by the number: `spec cvd-risk-assessment: Calculator bypass for statin benefit groups`.
- Suggestions are "for clinician–patient discussion", mapped to the ACC/AHA bands: `spec cvd-risk-assessment: Risk categories and management suggestions`.
- Retinal enhancers are investigational and never change the number: `spec cvd-risk-assessment: Risk enhancers`.
- Method is recorded with each result: `spec fhir-clinical-records: Resource mapping`.
- AHA PREVENT considered and rejected for demo scope (design D7).

NIST: Map, Measure. EU AI Act: Art. 10, 13, 15. **Residual: medium.** The coefficients have not been checked against the published paper (design Risks), and the oracle test uses published worked examples. PCE may overestimate risk for Thai patients. The AVR reference interval is a literature placeholder, and AutoMorph's AVR (0.55–0.59 on the gradable demo images, `app/api/demo_cache/*/meta.json`) falls below it, so the retinal enhancer flags every gradable demo image.

## Coverage by EU AI Act obligation

| Obligation | Where |
|---|---|
| Art. 9 Risk management | This register; H1, H2, H6 |
| Art. 10 Data governance | Consent purposes (H5), synthetic data only (`spec fhir-clinical-records: Synthetic Thai demo patients`), `docs/model-card.md` |
| Art. 12 Logging | `spec patient-data-protection: Access audit trail`, `spec fhir-clinical-records: AI provenance on every output` |
| Art. 13 Transparency | Labels, reasons, limitations, thresholds panel (`spec crao-emergency-triage: Configurable thresholds`) |
| Art. 14 Human oversight | `spec clinician-review: AI results are preliminary until signed` |
| Art. 15 Accuracy, robustness, cybersecurity | Quality gate (H3), monitoring (H6), access control (H5) |

This is a self-assessment against the listed obligations, not a conformity assessment. The prototype is not placed on the market.
