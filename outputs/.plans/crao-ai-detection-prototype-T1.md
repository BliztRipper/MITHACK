# T1 brief: CRAO / retinal artery occlusion AI literature
Write to outputs/.drafts/crao-ai-detection-prototype-research-literature.md

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
1. Other AI studies detecting CRAO/BRAO/RAO on colour fundus photos (2018-2026): architecture, n, AUC/sens/spec, external validation.
2. OCT-based AI for acute CRAO (inner retinal hyperreflectivity etc.); OCT vs fundus sensitivity at hyperacute stage.
3. Ultra-widefield, handheld, smartphone-based fundus AI for CRAO or emergency eye disease (e.g., FOTO-ED, non-mydriatic cameras in ED, Optomed). Performance on non-standard cameras.
4. Retinal foundation models (RETFound Nature 2023, VisionFM, FLAIR, RetiZero, etc.): do any report RAO/CRAO results or few-shot rare-disease performance?
5. Vision-language / LLM (GPT-4V, Gemini, Med-PaLM M, etc.) evaluated on fundus diagnosis, including any CRAO cases; how reliable?
6. Multimodal approaches combining image + clinical context (onset time, RAPD, symptoms) for CRAO or stroke-equivalent triage.
7. Concrete list of gaps in the base paper that later/other work addresses or that remain open.
