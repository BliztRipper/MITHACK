# T4 brief: prototype architecture and trustworthy-AI design
Write to outputs/.drafts/crao-ai-detection-prototype-research-build.md

## Context
Base paper: Gungor, Sarbout et al., "Artificial Intelligence-Based Detection of Central Retinal Artery Occlusion Within 4.5 Hours on Standard Fundus Photographs", J Am Heart Assoc 2025, doi 10.1161/JAHA.124.041441 (medRxiv 10.1101/2024.12.19.24319390; NCT06390579). Full text in /Users/arnon/Desktop/MITHACK/CRAO-AI-detection.md. Key facts: CNN, 4 classes (CRAO, CRVO, NAION, normal); 1,322 photos / 771 patients / 9 centres; training CRAO photos were 24 h–30 d after onset; hyperacute (<4.5 h) test AUC 0.96, sens 92.6%, spec 85.0%; beat 3 stroke neurologists (sens 50–63%); CLAHE on LAB L-channel + background subtraction (dilation + median blur); limitations: retrospective, excluded multi-pathology and poor-quality images, standard cameras only (no handheld/widefield/smartphone), no OCT, all test CRAO had abnormal fundus (may miss normal-fundus hyperacute CRAO).
Purpose: a hackathon team (Siriraj x MIT "Agentic Healthcare: From Models to Trustworthy Medicine", cardiovascular track, Thailand) wants to build an ENHANCED version and an EASY prototype in ~24-48 h.

## Rules
- Use alphaXiv paper tools (alpha_search / alpha_get_paper / alpha_ask_paper; alphaXiv is logged in), feynman_science_database_search (PubMed, Europe PMC, Semantic Scholar, OpenAlex), web_search and fetch_content.
- Every number: exact figure, population/dataset, year, direct URL/DOI/PMID/arXiv ID. Quote where possible.
- Flag conflicts; do not silently pick one number. Mark anything unsourced as UNVERIFIED. Never invent numbers, datasets, licences, or repos.
- If a PDF fails, continue from abstract/metadata and mark "PDF blocked".
- Output Markdown: Search terms used; Findings (bullet per claim + source); Implications for the enhanced version/prototype (label as inference); Conflicts/gaps; Sources (title, year, URL).

## Questions
1. Agentic clinical triage patterns: LLM agents that orchestrate image models + checklists + escalation (papers 2023-2026 on medical AI agents, tool-using agents in radiology/ophthalmology). What works, what fails (hallucination, overreliance)?
2. Image-quality gating for fundus (EyeQ, automated quality assessment) and why it matters for deployment (e.g., Google DR screening in Thailand: Beede et al. CHI 2020 field study; Ruamviboonsuk et al. prospective Thai DR AI study, Lancet Digit Health 2022). Extract the concrete lessons and numbers.
3. Uncertainty / selective prediction / OOD detection for medical imaging; calibration; "abstain and escalate" designs.
4. Explainability: Grad-CAM limits; what clinicians actually find useful.
5. Fast prototype stacks: Gradio vs Streamlit for medical image demos, Hugging Face Spaces, timm, fine-tuning on small datasets; typical compute/time for fine-tuning a ViT/ResNet on ~1-2k images.
6. Reporting and regulation: TRIPOD+AI (2024), CONSORT-AI/SPIRIT-AI, DECIDE-AI, WHO AI ethics guidance; Thai FDA software-as-medical-device and Thai PDPA rules for health images (if findable).
