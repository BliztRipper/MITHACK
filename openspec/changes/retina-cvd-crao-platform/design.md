# Design

## Context

See proposal.md (Why) for motivation and `specs/` for required behaviour.

Current state:
- `experiments/crao-prototype/` (about 330 lines of Python) holds a heuristic quality gate and the base paper's preprocessing (`vision.py`), the triage rules with 13 asserts (`triage.py`), an EfficientNet-B0 fine-tune script (`train.py`) and a Gradio UI (`app.py`). The triage rules have already been safety-reviewed (GCA branch, unknown onset, normal-photo rule) and must not regress.
- The repo has no app code, no git, and an empty `openspec/specs/`. Playwright is already a devDependency.
- Hardware: Apple M4 Pro, so PyTorch runs on MPS. Docker 29 is installed.
- AutoMorph (Apache-2.0) pins Python 3.11 and torch 2.3.1, says a GPU (CUDA or Apple MPS) is essential, and runs as a folder-in / CSV-out batch pipeline, not as a library.
- RETFound weights (`YukunZhou/RETFound_mae_natureCFP`) are gated on Hugging Face and licensed CC BY-NC 4.0.
- InterSystems kit (MIT): IRIS for Health Community in Docker, with FHIR R4 at `http://localhost:32783/csp/healthshare/demo/fhir/r4`.

Corrected user flow (replaces the original diagram). Consent and clinical inputs come before capture, and clinician sign-off sits between AI output and action:

```
patient arrives → clinician picks mode → consent check (PDPA) → clinical inputs
  → fundus capture/upload → EXIF strip → quality gate ──fail──→ RETAKE (+ urgent-referral fallback in Emergency)
  → segmentation (vessels, A/V, disc, fovea)
      ├─ Screening: vascular measurements → PCE → statin groups → enhancers → suggestions
      └─ Emergency: CRAO probability + heatmap → calibrated band → triage rules
  → explanation (templates) → PRELIMINARY result
  → clinician confirm / override (+reason) → FINAL report + patient summary (TH/EN)
  → monitoring (agreement, abstain, quality, drift) → offline retrain (consented cases) → new locked version
```

## Goals / Non-Goals

**Goals:**
- A stage demo that runs end to end on one laptop, with no internet needed after setup.
- Every clinical decision rule lives in plain, unit-tested Python. Models only produce numbers and maps.
- One record store (IRIS FHIR) that makes the InterSystems integration visible to judges.
- Honest outputs: placeholder thresholds and data limits are shown in the UI, not hidden.

**Non-Goals:**
- Hosted, multi-tenant or production deployment, HA, or a real identity provider.
- Validated clinical accuracy. The CRAO head is trained on about 151 public established-RAO images.
- Predicting CVD outcomes directly from the retina. No outcome-labelled data is available.
- Any LLM in the decision or explanation path.

## Decisions

### D1. Layout and runtime
```
app/
  api/        FastAPI service (Python 3.11): routes, rules, model wrappers, FHIR client
    rules/    triage.py (migrated), risk.py (PCE + statin benefit groups + enhancers), explain.py, templates/{th,en}.json
    vision/   quality.py + preprocess.py (migrated vision.py), segment.py (AutoMorph), crao_model.py, heatmap.py
    fhir/     client.py, mapping.py, seed.py
    tests/
  ml/         train.py (migrated), calibrate.py, export_reviewed.py
  web/        React + Vite + TypeScript + Tailwind
  fhir/       docker-compose.yml + IRIS setup adapted from the InterSystems kit (MIT, attributed)
docs/         model-card.md, risk-register.md, intended-use.md, pitch-notes.md
```
IRIS runs in Docker. The API runs natively so AutoMorph and the model can use MPS, since Docker on macOS has no GPU access. The web app uses the Vite dev server for the demo. *Alternative:* containerise everything. Rejected because inference would run on CPU and could take minutes per image on stage.

### D2. Backbone: RETFound first, EfficientNet-B0 fallback, same interface
`crao_model.py` loads whichever checkpoint is present (`arch` is stored in the checkpoint, as `train.py` already does). RETFound ViT-L is fine-tuned with layer-wise LR decay; only the last blocks are unfrozen because positives number about 151. The existing EfficientNet-B0 path stays as the guaranteed fallback if Hugging Face access is not granted in time. *Alternatives:* FLAIR (Apache-2.0, commercially safer). It is documented as the commercial swap in `pitch-notes.md` but not built now (YAGNI).

### D3. Calibration and bands
Temperature scaling is fitted on the validation fold (`ml/calibrate.py`). `P_LOW` is set to the highest threshold that keeps validation sensitivity at or above 0.95, and `P_HIGH` is set for specificity at or above 0.90. Both are written to the checkpoint and still labelled "placeholder, not clinically validated". Reported metrics come from 5-fold CV with 95% CIs, and web-crawled images are kept in a separate split (leakage rules from the prototype README). *Alternative:* conformal prediction sets. These give a stronger guarantee, but the band UI already expresses abstention, and n is too small for the guarantee to mean much.

### D4. Heatmap
Grad-CAM through `pytorch-grad-cam` (MIT). It uses a ViT reshape transform for RETFound and the last conv block for EfficientNet. The heatmap is returned as an RGBA PNG at image resolution. *Alternative:* attention rollout. It works only for ViT, so a fallback model would need a second code path.

### D5. Segmentation and vascular measurements via AutoMorph
AutoMorph is vendored as a git submodule under `app/api/vision/automorph/` and called by `segment.py` on a per-request temp directory (M0 preprocess → M2 vessel, A/V, disc → M3 features). Outputs: vessel, A/V and disc masks (RGBA overlays), disc centre and diameter, and CRAE, CRVE and AVR (zone B). **AVR is the primary enhancer** because it is unitless. CRAE and CRVE need a pixel-to-µm scale that varies by camera, so they are displayed but not used for flags. AutoMorph's M1 quality grade is combined with the existing heuristic score: an image passes only if both pass. A spike measures latency first (task 2.1). If AutoMorph exceeds about 20 s per image on MPS, only M2 vessel and disc run live, and demo images are pre-computed (D11). *Alternative:* a Frangi vesselness filter. It is shallow (no A/V and no disc), so it is kept only as the emergency fallback.

### D6. Region-based explanation
Fovea = disc centre + 2.5 disc diameters toward the temporal side. Laterality is inferred from the disc position in the image, and the fovea is placed 0.3 DD inferior. Regions are circles: disc (r = 1 DD), macula (r = 1 DD around the fovea), arcades (vessel mask dilated, excluding the first two regions) and periphery (the rest of the field of view). `explain.py` computes the fraction of heatmap mass in each region, picks the top region, and fills fixed sentences from `templates/{en,th}.json` keyed by (mode, band, region). The limitation sentences are always appended. If no disc is found, only the probability, band and limitations are reported.

### D7. Risk equations as pure functions with oracle tests
`risk.py`: `pce(inputs) -> Result` uses the Goff 2013 coefficients (white equation unless the patient is African American). `categorise()` and `suggestions()` turn bands into suggestion text. `statin_group()` returns the 2018 AHA/ACC statin benefit group (known ASCVD, LDL ≥190, diabetes 40–75 with LDL ≥70) before any band is used. Test oracle: the four 2013 ACC/AHA published worked examples. Input ranges: PCE ages 40–79, TC 130–320, HDL 20–100 and SBP 90–200. Values outside a range produce "not valid", never a clamped number. *Alternative:* the AHA PREVENT equations (2023). Rejected for demo scope: PCE is built and matches the published examples, while PREVENT needs eGFR and BMI inputs and new equations.

### D8. FHIR as the only clinical store
`fhir/client.py` is a thin `httpx` wrapper over FHIR REST that works on plain dicts. Each case save is one **transaction Bundle**, so it is all or nothing (spec: no partial saves). The mapping follows the spec's resource list. AI outputs reference one `Device` per model version. Clinicians are `Practitioner` resources, and app users map to them. Drift alerts and incidents are `Flag` resources (category `drift` / `ai-incident`). Monitoring queries DiagnosticReport and Observation by `device` and date and aggregates in Python, which is fine at demo volume. *Alternatives:* SQLite plus a FHIR export. Rejected because the user chose FHIR as the database. The `fhir.resources` pydantic models were also rejected as needless weight for about 12 resource shapes.

### D9. Biometric image protection by crypto-shredding
Images and overlays are encrypted with AES-256-GCM (`cryptography`) using a **per-patient data key**. Data keys are wrapped by a master key from the `APP_MASTER_KEY` environment variable and kept in a local key file (`app/api/.keys/keys.json`), which is outside FHIR so the keys never land in FHIR history. Media holds the ciphertext with an extension recording the algorithm and key id. On consent withdrawal the API deletes the Media resources **and destroys the patient's data key**. Copies left in FHIR version history then become undecryptable, which works around the server keeping history on delete. *Alternative:* IRIS `$expunge` or purge. Its availability in the Community edition is unverified, and it would bind erasure to one vendor.

### D10. Auth, roles, audit
Demo users and bcrypt hashes live in `app/api/users.yaml` (frontline GP, ophthalmologist reviewer, admin). Sessions are signed HTTP-only cookies with a 30-minute sliding expiry. A FastAPI dependency enforces the role per route. A middleware writes one `AuditEvent` per patient-data request (user, role, action, resource, outcome). The API exposes no update or delete for AuditEvent, and IRIS is bound to localhost only. *Limitation (stated in the risk register):* an IRIS superuser can still edit records, and the demo has no tamper-evident log.

### D11. Demo reliability
`app/api/demo_cache/` stores pre-computed outputs (masks, heatmap, measurements, probability) for 6 curated CC BY images: 2 RAO, 1 CRVO mimic, 1 normal, 1 poor quality, 1 hypertensive-looking. They are keyed by image SHA-256, and the API uses the cache when the hash matches, so stage latency stays under 2 s. Live inference handles any other upload.

### D12. Frontend
Pages: Login · Patients (search) · Patient · New case wizard (mode → consent → inputs → upload → result) · Result (stacked image layers with per-layer toggle and opacity slider, side-by-side compare, band gauge, explanation, triage card or risk panel) · Sign/Override dialog · Review queue · Monitoring · About (thresholds, model card). Overlays are absolutely positioned RGBA PNGs over the base image, so the browser composites them with no canvas code. The report uses a print stylesheet and `window.print()`. The UI is in English with a Thai patient summary. Full Thai UI localisation is deferred.

### D13. Prototype migration
`triage.py` moves under `rules/` unchanged apart from imports. Its 13 `__main__` asserts become pytest cases, plus the new RETAKE urgent-referral fallback (spec change). `vision.py` splits into `quality.py` and `preprocess.py`. `train.py` moves to `ml/`. `experiments/crao-prototype/` is deleted once the ported tests pass.

## Risks / Trade-offs

- [The CRAO model is trained on established RAO only, so it may miss hyperacute cases] → The normal-photo rule escalates fitting stories, the UI always states the limitation, and the pitch claims workflow value rather than 4.5 h accuracy.
- [About 151 positives means overfitting and wide CIs] → Use 5-fold CV with CIs, report on a separate web-crawled split, and keep placeholder labels on thresholds.
- [The heatmap highlights spurious regions, and clinicians over-trust it] → Show it with segmentation and a "model attention, not lesions" label, explain by anatomical region, and require sign-off.
- [AutoMorph is slow or brittle] → Latency spike first, then the M2-only path, the demo cache, and Frangi as a last resort.
- [RETFound access is not granted in time] → Use the EfficientNet-B0 fallback, which needs the same interface and no code change.
- [RETFound CC BY-NC blocks commercial use] → Use it only for the demo, and put the licence or FLAIR swap in pitch notes.
- [PCE overestimates risk for Thai patients] → Show the PCE Asian-population caveat on every result. Ages 30–39 get no risk number.
- [PCE coefficients were transcribed without access to the paper] → Check them against Goff 2013 Table A before the demo.
- [AVR reference intervals for Thai adults are unverified] → Use literature placeholders labelled as such, and list them as an open question.
- [IRIS is down on stage] → Run a start-up health check that shows a clear banner. The analysis still renders and saving is blocked, with no silent loss.
- [Automation bias with GPs accepting every AI output] → Overrides need reasons, monitor the agreement rate, and alert on near-100% agreement as a rubber-stamping signal (same drift mechanism).

## Migration Plan

1. Bring up IRIS with `docker compose -f app/fhir/docker-compose.yml up -d`, then run the seed.
2. Start the API (`uvicorn`) natively with MPS, then start `npm run dev` in `app/web`.
3. Remove `experiments/crao-prototype/` after the ported tests pass. Rollback means restoring the folder, which has no data dependencies.

## Open Questions

- AVR reference interval for Thai adults: literature placeholder until a Thai or Asian cohort value is found. Only a config value changes.
- Suggestion text follows the 2018 AHA/ACC cholesterol guideline. Any local adaptation is config text, with no code change.
- Whether Thai medical-record law requires keeping the signed report after withdrawal: current behaviour keeps the report text and erases images, which a legal check should confirm.
- RETFound Hugging Face access timing: this decides which backbone ships, but there is no code impact (D2).
