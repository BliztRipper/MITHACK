# T2 brief: CRAO clinical pathway, trials, and system gaps
Write to outputs/.drafts/crao-ai-detection-prototype-research-clinical.md

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
1. AHA 2021 scientific statement on CRAO management (Mac Grory et al., Stroke 2021): key recommendations (stroke-centre referral, time windows, work-up).
2. Thrombolysis evidence: THEIA (alteplase <4.5 h) final results, TenCRAOS (tenecteplase), REVISION (alteplase up to 12 h?), meta-analyses (Shahjouei 2024; Mac Grory 2020), and any 2025-2026 guideline updates. Report the actual efficacy results.
3. Stroke/MI risk after CRAO (timing, peak first 7 days), share with silent brain infarcts on MRI; recommended secondary-prevention work-up (carotid imaging, ECG/AF monitoring, echo, GCA ESR/CRP).
4. Diagnostic delay data: time from onset to presentation, % seen by ophthalmologist, ED misdiagnosis, nonophthalmic physician confidence; teleophthalmology/telestroke models (e.g., FOTO-ED, eye-stroke protocols, "eye stroke code").
5. Incidence of CRAO (per 100,000) globally and any Thai/Asian data; Thai stroke fast-track and whether CRAO is included; ophthalmologist distribution in Thailand.
6. Giant cell arteritis as a must-not-miss cause (arteritic CRAO) and how pathways handle it.
