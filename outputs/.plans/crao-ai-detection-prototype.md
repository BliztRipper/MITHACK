# Plan: Enhanced CRAO AI detection + easy hackathon prototype

Slug: `crao-ai-detection-prototype`
Date: 2026-10-17
Input: `CRAO-AI-detection.md` (Gungor, Sarbout et al., JAHA 2025, "AI-Based Detection of CRAO Within 4.5 Hours on Standard Fundus Photographs"; 1,322 photos, 771 patients, 9 centres; hyperacute AUC 0.96, sens 92.6%, spec 85.0%; beat 3 stroke neurologists on 120 photos).
Context: Siriraj x MIT "Agentic Healthcare: From Models to Trustworthy Medicine", CVD track (CRAO = "eye stroke").

## Key questions
1. **Gaps in the base paper.** What does it fail to cover (normal-fundus hyperacute CRAO, OCT, handheld/smartphone/widefield cameras, multi-pathology eyes, prospective validation, Asian populations, no clinical context)?
2. **State of the art since then.** Other CRAO/RAO AI work: OCT-based, smartphone/handheld fundus, ultra-widefield, retinal foundation models (RETFound etc.), multimodal (image + symptoms + time), LLM/vision-language for fundus.
3. **Clinical pathway.** CRAO as a stroke equivalent: AHA 2021 statement, time windows, latest thrombolysis RCT results (THEIA, TenCRAOS, REVISION), stroke work-up after CRAO, ED/ophthalmology access gaps, any Thai data.
4. **Enhancement options** ranked by impact × hackathon feasibility: agentic triage workflow (onset-time capture, stroke code activation, teleophthalmology escalation, secondary-prevention checklist), image-quality gating, uncertainty/abstention, explainability, multimodal inputs.
5. **Prototype building blocks.** Public fundus datasets with CRAO/RAO labels and their licences; pretrained weights (RETFound, timm/ImageNet); preprocessing (CLAHE, background subtraction); UI stack (Gradio/Streamlit); what can be built and demoed in ~24–48 h.
6. **Trustworthiness and regulation.** Failure modes, calibration, OOD detection, human-in-the-loop, reporting guidelines (TRIPOD+AI, CONSORT-AI), Thai FDA SaMD/PDPA (if findable).

## Evidence needed
- Base paper details plus the medRxiv preprint; NCT06390579.
- Papers 2020–2026 on AI for CRAO/RAO (fundus, OCT, UWF, smartphone) with metrics and n.
- Thrombolysis RCT results for CRAO, 2024–2026.
- Dataset pages (RFMiD, JSIEC/Cen 39-class, ODIR, Kaggle retinal disease sets, EyePACS AIROGS) with CRAO/RAO label counts and licences.
- RETFound and other retinal foundation model repos and weights licences.
- Guidance on clinical AI trustworthiness.

## Scale decision
Multi-domain (ML literature + clinical trials/pathway + datasets/models + prototype engineering). Not a "what is X" explainer. **Decision: 4 `researcher` subagents in parallel**; lead writes synthesis and builds a minimal prototype skeleton; then `verifier`, then `reviewer`.

## Task ledger
| ID | Owner | Task | Output | Status |
|---|---|---|---|---|
| T1 | researcher | CRAO/RAO AI literature: fundus, OCT, UWF, smartphone, foundation models, multimodal; metrics; gaps vs base paper | outputs/.drafts/crao-ai-detection-prototype-research-literature.md | done (child stopped by session reload AFTER writing; file complete) |
| T2 | researcher | Clinical pathway: AHA statement, thrombolysis RCTs (THEIA, TenCRAOS, REVISION...), stroke risk after CRAO, ED diagnostic gap, telemedicine, Thai context | outputs/.drafts/crao-ai-detection-prototype-research-clinical.md | done |
| T3 | researcher | Data + models: public datasets with CRAO/RAO labels and licences; pretrained retinal models (RETFound etc.); smartphone/handheld fundus devices | outputs/.drafts/crao-ai-detection-prototype-research-data.md | done (child stopped by session reload AFTER writing; file complete) |
| T4 | researcher | Prototype + trust: agentic triage design patterns, quality gating, uncertainty/OOD, Grad-CAM, UI stacks, reporting/regulatory guidance | outputs/.drafts/crao-ai-detection-prototype-research-build.md | done |
| P1 | lead | Minimal runnable prototype skeleton (preprocessing from paper + triage agent logic + UI), with a self-check | experiments/crao-prototype/ | done (README pending datasets) |
| S1 | lead | Synthesis draft | outputs/.drafts/crao-ai-detection-prototype-draft.md | done |
| C1 | verifier | Citations + URL check | outputs/.drafts/crao-ai-detection-prototype-cited.md | done by lead (verifier timed out at 30 min, no output; lead finished from its partial artifacts) |
| R1 | reviewer | Verification review | outputs/.drafts/crao-ai-detection-prototype-verification.md | done (0 FATAL / 6 MAJOR / 11 MINOR; all addressed in -revised.md) |
| D1 | lead | Deliver final + provenance | outputs/crao-ai-detection-prototype.md | done |

## Verification log
- 2026-10-17: Workflow 0fae5747 launched (4 researchers, async). Data researcher flagged for a 240 s bash call (RFMiD 2.0 download); checked the log, it had already moved on, so no action taken.
- 2026-10-17: Prototype verified in /tmp/crao-venv (torch 2.14.1, timm 1.0.30, gradio 6.30.0, opencv 5.0.0): `vision.py` self-check OK (quality good 0.91 / blurry 0.03 / dark 0.00), `triage.py` self-check OK (10 asserts), `train.py` ran 1 epoch on 16 synthetic images and saved weights, app `run()` passed for the no-model, GCA, low-quality and model paths. Bug found and fixed: DataLoader workers can't pickle the lambda transform on macOS (spawn) → num_workers=0. Synthetic-data metrics are meaningless and are NOT reported.

- 2026-10-17: Workflow 0fae5747 result: build and clinical completed ok; literature and data show "stopped: extension session was replaced or reloaded", but both files on disk are complete (Findings, Sources and Coverage sections present; 32 KB and 28 KB). Accepted as-is; no rerun.
- 2026-10-17: Research changed the prototype. Thrombolysis RCTs THEIA/TenCRAOS were null, REVISION stopped for futility, AHA 2026 = 2b "uncertain" → triage card reworded to "activate stroke team; thrombolysis benefit uncertain". GCA → "NOT a thrombolysis candidate". Self-checks rerun OK; Gradio server returned HTTP 200 with the app title.
- 2026-10-17: Verifier 7b791425 TIMED OUT (1,800 s) without writing the cited file. Its partial artifacts in /tmp/crao_cite (sources.tsv: 77-source tag→URL map; status.txt) were reused. Lead re-verified every identifier through registries: 23 DOIs (doi.org handle API), 21 PMIDs (E-utilities esummary), 7 arXiv (abs-page citation_title, after API 429/redirects), 6 GitHub (API 200), 1 Zenodo (API), 18 web pages (HTTP 200/303); 3 publisher 403s resolved via DOI handle or Zenodo API; L19 added (DOI OK). Result: 0 unresolvable. Base-paper numbers spot-checked against CRAO-AI-detection.md (AUC 0.96, sens 92.6%, 4/54 missed, spec 85.0%, neurologists 50–63.3%); fixed the training-set wording (614 photos from 517 patients + 425 public = 1,039). Cited file: 76 sources, 0 orphans. Side issue: a stray Gradio server (PID 82056) left by a non-matching pkill was killed.

- 2026-10-17: Review applied. triage.py: unknown onset with a low score and sudden loss now ESCALATEs; GCA caps the card at URGENT, GCA step first, no stroke-team/lysis text; 13 asserts pass; requirements pinned. The report was revised via 26 asserted replacements plus 2 Open Questions; 0 orphans. Final = -revised.md copied to outputs/.

## Decision log
- 2026-10-17: Slug `crao-ai-detection-prototype`.
- 2026-10-17: Scale = 4 researchers. alphaXiv is now logged in (`feynman alpha status`), so researchers can use the alpha paper tools.
- 2026-10-17: Local env has no torch/cv2. The prototype must either use lightweight deps or document the install; any model performance claims must come from sources, never from the prototype (no trained weights → no metrics).
