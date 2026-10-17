# Tasks

## 1. Setup and risk spikes

- [ ] 1.1 Request Hugging Face access to `YukunZhou/RETFound_mae_natureCFP` and record the request date in `docs/model-card.md`; verify the request shows as pending or granted on the model page
- [x] 1.2 Create the `app/{api,ml,web,fhir}` and `docs/` layout from design D1, with a Python 3.11 venv and `app/api/requirements.txt` (fastapi, uvicorn, torch 2.3.1, torchvision, timm, opencv-python-headless, numpy, httpx, cryptography, bcrypt, itsdangerous, pyyaml, pytorch-grad-cam, pytest); verify `python -c "import torch; print(torch.backends.mps.is_available())"` prints True
- [x] 1.3 Add AutoMorph as a git submodule under `app/api/vision/automorph/`, download its weights, and run it on 3 sample fundus images on MPS; verify masks and the features CSV are produced and record per-image latency in `docs/model-card.md` (decides full pipeline vs M2-only per design D5)
- [x] 1.4 Adapt the InterSystems kit's IRIS for Health Docker setup into `app/fhir/docker-compose.yml` (bound to 127.0.0.1, MIT attribution in `app/fhir/README.md`); verify `curl http://localhost:32783/csp/healthshare/demo/fhir/r4/metadata` returns a CapabilityStatement
- [ ] 1.5 Download Mendeley RAO v2 and RFMiD 1.0 into `data/` (gitignored) and arrange `data/{train,val}/{crao,other}` per the prototype README's leakage rules (RFMiD RAO dropped from "other", web-crawled images in a separate split); verify the class counts printed by a short count script match the README

## 2. Clinical rules (pure Python, no I/O)

- [x] 2.1 Move `triage.py` to `app/api/rules/triage.py` and convert its 13 `__main__` asserts to `tests/test_triage.py`; verify `pytest tests/test_triage.py` passes with all 13 cases
- [x] 2.2 Add the Emergency-mode RETAKE urgent-referral fallback action and the reasons format from the crao-emergency-triage spec, plus tests for the quality-override and reasons scenarios; verify pytest passes
- [ ] 2.3 Generate `tests/fixtures/thai_cv_oracle.json` (20 input/expected rows) by running the Ramathibodi `formular.js` in Node, recording source URL and fetch date in the fixture; verify the file holds 20 rows covering all three variants
- [ ] 2.4 Implement `rules/risk.py` `thai_cv()` (TC variant, else waist-to-height, age 30–70 validity) and verify every oracle row matches within 0.1 percentage point in `tests/test_risk.py`
- [x] 2.5 Implement `pce()` with Goff 2013 coefficients, input ranges and the population caveat; verify the four published ACC/AHA worked examples match within 0.1 percentage point and out-of-range inputs return "not valid"
- [x] 2.6 Implement risk bands, management suggestion text, stage 1 hypertension labelling, statin-benefit-group bypass (known ASCVD, LDL ≥190), risk enhancers (AVR flag, unchanged risk number) and the arcus senilis prompt; verify one test per cvd-risk-assessment scenario passes
- [x] 2.7 Create `rules/templates/en.json` and `th.json` (explanation sentences keyed by mode/band/region, limitation sentences, patient summaries) and document all thresholds with "placeholder" status in `app/api/config.yaml`; verify a test loads both templates and finds every key used by the rules

## 3. FHIR record store and data protection

- [x] 3.1 Implement `fhir/client.py` (httpx: read, search, transaction Bundle, history, delete) with a start-up health check; verify a test against the running IRIS round-trips a Patient and that a failed transaction leaves no resources behind
- [x] 3.2 Implement `fhir/mapping.py` for Patient, Practitioner, Consent (care + model-improvement purposes), Encounter, Media, Observation (LOINC codes from the fhir-clinical-records spec), Condition, RiskAssessment, DiagnosticReport, Device, Provenance, AuditEvent and Flag; verify a test builds a full Screening and an Emergency case Bundle and IRIS accepts both
- [ ] 3.3 Implement `fhir/seed.py` loading 20 synthetic Thai patients (Thai names, ages 30–79, mixed risk, recent vitals/labs, 3 with prior signed screenings) using conditional create so it is idempotent; verify running it twice leaves exactly 20 patients
- [ ] 3.4 Implement per-patient AES-256-GCM image encryption with master-key-wrapped data keys in `.keys/keys.json` (design D9); verify a test shows the stored Media payload is not a decodable image and decrypts correctly with the key
- [ ] 3.5 Implement consent withdrawal: delete Media, destroy the patient data key, strip image references from signed reports, set Consent inactive; verify a test shows images (including FHIR history versions) can no longer be decrypted while report text remains

## 4. Vision pipeline and model

- [ ] 4.1 Split `vision.py` into `vision/quality.py` and `vision/preprocess.py`, add EXIF/GPS stripping, file type and 20 MB checks, a non-fundus check (field-of-view circle) and named retake reasons; combine with AutoMorph M1 grade (both must pass); verify tests with a dark, a blurred, a face and a good image give the expected accept/reason
- [ ] 4.2 Implement `vision/segment.py` wrapping AutoMorph (per-request temp dir) to return vessel, A/V and disc RGBA overlays, disc centre/diameter, CRAE, CRVE and AVR; verify on a sample image that overlays align with the image size and AVR is a number in (0.3, 1.5)
- [ ] 4.3 Move `train.py` to `app/ml/`, add the RETFound ViT-L path (last-block fine-tune, layer-wise LR decay) beside the EfficientNet-B0 path, and 5-fold CV reporting with 95% CIs; verify a run produces `model.pt` and a metrics JSON (use EfficientNet-B0 if RETFound access is still pending)
- [ ] 4.4 Implement `ml/calibrate.py` (temperature scaling on the validation fold; P_LOW for sensitivity ≥0.95, P_HIGH for specificity ≥0.90) writing temperature, thresholds and calibration date into the checkpoint; verify validation-set ECE before/after is printed and the checkpoint holds the fields
- [ ] 4.5 Implement `vision/crao_model.py` (load any checkpoint arch, calibrated probability, band, "no model loaded" degradation) and `vision/heatmap.py` (Grad-CAM, ViT reshape transform for RETFound); verify tests for missing weights → None and that a heatmap PNG matches the input size
- [ ] 4.6 Implement `rules/explain.py`: fovea estimate from disc and laterality, region masks, heatmap mass per region, template fill, limitations always appended, region omitted when no disc; verify tests with synthetic heatmaps centred on macula vs disc pick the right region
- [ ] 4.7 Write `docs/model-card.md` (intended use, training data and licences, CV metrics with CIs, calibration, thresholds as placeholders, known failure modes: hyperacute, poor images, mimics) from the 4.3/4.4 outputs; verify every number in it matches the metrics JSON

## 5. API

- [ ] 5.1 Implement login/logout with `users.yaml` (bcrypt), signed HTTP-only session cookie with 30-minute sliding expiry, and role dependencies (gp, reviewer, admin); verify tests for 401 without session, expiry after idle, and 403 for admin image access
- [ ] 5.2 Implement the audit middleware writing one AuditEvent per patient-data request with no image bytes or names in logs; verify a test that opening an image creates a read AuditEvent and that an analysis exception log line contains only case id and error
- [ ] 5.3 Implement patient search/detail and consent endpoints (record, check, withdraw); verify tests that upload is refused without consent and allowed after consent
- [ ] 5.4 Implement `POST /cases` (mode + inputs + image → quality gate → segmentation → Screening: measurements + risk, or Emergency: probability + heatmap + triage → explanation) saving a preliminary case as one transaction, with demo-cache lookup by SHA-256 (design D11); verify an end-to-end API test for each mode and for a RETAKE image returns the spec'd fields
- [ ] 5.5 Implement review endpoints: queue (Emergency first, ESCALATE visible to reviewers), confirm, override with required reason, amend (status amended, history kept), Provenance on sign; verify tests for each clinician-review and report-status scenario
- [ ] 5.6 Implement monitoring endpoints: metrics per model version and period, calibration summary with the 30-case minimum, rolling-50 drift alerts (quality, uncertain, override, agreement upper limit) as Flags with acknowledge, incident flag/close, and de-identified consented export (zip + labels CSV, audited); verify tests for each model-monitoring scenario
- [ ] 5.7 Populate `app/api/demo_cache/` for the 6 curated CC BY images with attribution in `demo_cache/SOURCES.md`; verify each cached case returns in under 2 s via `POST /cases`

## 6. Web app

- [ ] 6.1 Scaffold `app/web` (React + Vite + TS + Tailwind) with an API client, login page and role-aware navigation; verify login as each demo user shows the right menu
- [ ] 6.2 Build Patients search and Patient detail (prior cases, consent status, withdraw consent); verify a seeded patient with prior screening shows the prior case
- [ ] 6.3 Build the New case wizard: mode → consent gate/form → mode-specific inputs (pre-filled with dates, range validation) → upload with quality result and retake reason; verify by manual run that a poor image shows the retake reason and that blocked consent shows the form
- [ ] 6.4 Build the Result view: stacked layers (vessels, A/V, disc, heatmap) with toggles, opacity slider and side-by-side compare, band gauge with model version, explanation, "model attention, not lesions" label, and the triage card or risk panel (Thai CV + PCE, caveat, enhancers, suggestions); verify against a cached RAO image and a cached screening image
- [ ] 6.5 Build the Sign/Override dialog, print-stylesheet report (`window.print()`), and Thai/English patient summary; verify an override without a reason is blocked and the printed page shows every report section
- [ ] 6.6 Build the Review queue, Monitoring dashboard (metrics, calibration panel, alerts with acknowledge, incidents) and About panel (thresholds with placeholder status, model card link); verify the dashboard shows "insufficient data" with the seeded case count

## 7. Governance documents

- [ ] 7.1 Write `docs/intended-use.md` (users: frontline non-ophthalmologist clinicians; decision support only; not for diagnosis; contraindications) and `docs/risk-register.md` mapping each hazard (missed CRAO, false CRAO, poor image, automation bias, data breach, drift, PCE miscalibration) to mitigations in the app and to NIST AI RMF functions and EU AI Act high-risk obligations (risk management, data governance, logging, transparency, human oversight, accuracy/robustness); verify each mitigation names a spec requirement that exists
- [ ] 7.2 Write `docs/pitch-notes.md`: corrected user flow, why risk-enhancer framing, data ceiling statement, PDPA biometric handling, business model (per-screen fee via existing DR-screening sites / hospital SaaS), Thai FDA SaMD path, RETFound licence and FLAIR swap; verify every claim cites a spec, design decision or source

## 8. Integration and migration

- [ ] 8.1 Add one Playwright e2e test in `tests/frontend/`: login as GP → seeded patient → Emergency case with a cached RAO image → heatmap visible → sign with override → report shows final status; verify `npx playwright test` passes with IRIS, API and web running
- [ ] 8.2 Run the full stack from a clean start per design Migration Plan steps 1–2 and walk both modes plus consent withdrawal by hand; verify the AuditEvents and FHIR resources for the walkthrough exist in IRIS
- [ ] 8.3 Delete `experiments/crao-prototype/` once 2.1, 2.2 and 4.1 tests pass, and update `outputs/crao-ai-detection-prototype.md` references to point at `app/`; verify `grep -r "experiments/crao-prototype"` finds no live code references

## Workflow follow-up

- Archive the change with `/opsx-archive` after the demo build is reviewed.
