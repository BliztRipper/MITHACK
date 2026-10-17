# T3 brief: datasets, pretrained models, and capture hardware
Write to outputs/.drafts/crao-ai-detection-prototype-research-data.md

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
1. Public fundus datasets containing CRAO/BRAO/RAO labels, with counts and licences: RFMiD / RFMiD 2.0, JSIEC (Cen et al. Nat Commun 2021 "39 fundus diseases"), ODIR-5K, Kaggle retinal disease sets (the "Kaggle" set used in the base paper), FIVES, MuReD, EyePACS AIROGS (normal), APTOS, Messidor, others. Download URL, licence (commercial/non-commercial), image counts per class.
2. Datasets for the differential classes (CRVO, NAION/disc oedema, normal) and image-quality datasets (EyeQ).
3. Pretrained retinal models with downloadable weights and licences: RETFound (CFP and OCT), VisionFM, RetiZero, FLAIR, others on Hugging Face. Fine-tuning recipe and compute needed; few-shot results on rare classes if reported.
4. Smartphone / handheld fundus capture options usable in a Thai ED or community hospital (e.g., Optomed Aurora, D-EYE, smartphone adapters), image quality vs desktop cameras, approximate cost if officially listed.
5. Is the base paper's model/code/data public? (paper says data on request.)
