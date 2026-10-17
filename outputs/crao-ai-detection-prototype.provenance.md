# Provenance: Enhanced CRAO AI detection + easy hackathon prototype

- **Date:** 2026-10-17
- **Rounds:** 1 evidence round (4 parallel researchers), 1 lead synthesis, 1 citation pass, 1 review pass, 1 revision
- **Base input:** `CRAO-AI-detection.md` (Gungor, Sarbout et al., JAHA 2025, doi 10.1161/JAHA.124.041441)
- **Sources consulted:** ~180 across the four research notes (literature 36, clinical 52, data 30, build 42 numbered sources, with overlap), plus several hundred screened search hits (e.g. 139 LLM/fundus PubMed abstracts screened for RAO)
- **Sources accepted:** 76 in the final report. All 76 resolve: 23 DOIs (doi.org handle API), 21 PMIDs (NCBI E-utilities), 7 arXiv papers (abs-page titles), 6 GitHub repos (API), 1 Zenodo record (API), 18 web pages (HTTP 200/303). Three publisher 403s were resolved via the DOI handle or Zenodo API.
- **Sources rejected or downgraded:** Optomed CRAO page (vendor marketing, no data); ARVO 2025 abstract by Lam et al. and Stroke 2025 TP172 (blocked, no results); UWF RAO AUC 1.000 (3 test images, not informative); reseller camera prices (unverified); the NHSO "0.53%" rt-PA rate (likely extraction artefact, not used).
- **Verification:** PASS WITH NOTES
  - The verifier subagent timed out (30 min) without output. The lead completed citation from its partial artifacts and re-verified every identifier via registries.
  - The reviewer subagent found 0 FATAL, 6 MAJOR and 11 MINOR issues. All were addressed in `-revised.md`:
    - Two were code safety bugs, fixed in `triage.py` (unknown onset now escalates; GCA caps the card at URGENT with no thrombolysis text). 13 asserts now pass.
    - W1 (mixed test sets in the neurologist comparison), W4 (licence caveat), W5 (infarct range widened to 7–32%) and W6 (n=16 study) were reworded.
    - W2's 24 h cutoff and W4's licensing remain Open Questions 6–7.
  - No second review pass was run, because there were no FATAL issues.
- **Not verified:** any model accuracy (no real data trained); Thai CRAO incidence; CRAO eligibility for the NHSO stroke fast track; the AHA 2026 primary text (secondary quote only); RetiZero per-class RAO numbers.
- **Prototype checks (command output):** `experiments/crao-prototype/`, venv /tmp/crao-venv (torch 2.14.1, timm 1.0.30, gradio 6.30.0, opencv 5.0.0, now pinned). Results: triage self-check OK (13 asserts); vision self-check OK; `train.py` 1 epoch on synthetic data saved weights (metrics not reported); app `run()` passed on all paths; Gradio server returned HTTP 200. A macOS DataLoader pickling bug was found and fixed.
- **Plan:** outputs/.plans/crao-ai-detection-prototype.md
- **Research files:** outputs/.drafts/crao-ai-detection-prototype-research-literature.md, -research-clinical.md, -research-data.md, -research-build.md; draft -draft.md; cited -cited.md; review -verification.md; final candidate -revised.md
