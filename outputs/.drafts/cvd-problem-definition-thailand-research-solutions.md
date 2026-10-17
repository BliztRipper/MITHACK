# T4 Research notes: current solutions and shortcomings

Author: lead (degraded mode). Date: 2026-10-16.

## Search terms used
- PubMed: "Perez MV[au] large-scale assessment smartwatch identify atrial fibrillation"; "Yao X[au] artificial intelligence-enabled electrocardiograms low ejection fraction"; "McManus RJ[au] TASMINH4..." (no direct hit; dropped); "Thailand older adults smartphone digital health literacy" (irrelevant hits)
- Europe PMC: chatbot / VHV / telehealth Thai titles (see T3)
- curl WHO publication page: https://www.who.int/publications/i/item/9789240029200
- Europe PMC: 'TITLE:(thrombolysis AND Thailand)' (Lao teleconsultation)

## Findings: what exists today and where it falls short

| Current solution | Evidence it works | Documented shortcoming | Source |
|---|---|---|---|
| Universal Coverage Scheme: free primary care incl. HTN treatment | Thai IHD prevalence among hypertensives fell 56.6→34.5/1,000 (2011–2018) | HTN awareness 51.5%, control 22.7% and falling (2019–20) despite free care | PMID 41766720; 39538168 |
| Population screening / NHES-style measurement | Captures undiagnosed burden | ~half of hypertensives and ~37% of diabetics unaware | PMID 39538168; 40866600 |
| Thai CV risk score | Used as an outcome in Thai trials | DSMES cluster RCT (n=693) showed no change in Thai CV risk score or HbA1c vs control at 12 months for nurse-led or peer-assisted arms | PMID 42212245 |
| Health-literacy / chatbot HTN programs | Small RCT (n=58) lowered MAP 108.9 vs 111.4 mmHg; chatbot quasi-experiment (n=68) improved adherence and BP | Small, short, non-randomised or single-region; authors call chatbot findings "preliminary" | PMID 42375857; 42820082 |
| VHV-delivered education apps (LINE sticker) | Raised VHV stroke knowledge (n=60) | Knowledge outcome only; no patient-outcome data | PMID 39297115 |
| Community telehealth NCD risk assessment by community leaders | Feasible, 92–97% acceptability (n=120) | Feasibility only | PMID 42405357 |
| Stroke fast track (hospital-side) | Cut time to CT from ~2.5 h | Fixes in-hospital time; cannot fix 70% arriving >3 h; rt-PA 5.5% of IS in an early academic series | PMID 21122006; 36240046 |
| STEMI reperfusion expansion under UCS | PCI reach grew to 37 provinces with >50% PCI by 2017; reperfusion lowers 30-day mortality 14–20 pp | Non-reperfused patients' mortality rising; treatment-time medians 4–6 h in registries | PMID 32143572; 22612004 |
| Digital emergency referral (HIS.SANSAI, N. Thailand) | Referring hospitals rated "reducing coordinated time" 8.0/10 | Receiving hospitals rated "ease of use when recording" 4.27/10 | PMID 40840931 |
| Telestroke consultation (Thailand → Lao PDR) | 10 thrombolysed patients, 70% good outcome | Only 14% of 205 arrived within 4.5 h | PMID 31530479 |
| Smartwatch AF detection (Apple Heart Study) | 0.52% notified; PPV 0.84 for concurrent AF | Only 450 of 2,161 notified returned analysable patches; 34% had AF on patch; US, tech-owning, younger population | PMID 31722151 |
| AI-ECG for low EF (EAGLE, pragmatic RCT) | Diagnosis of low EF 2.1% vs 1.6% (OR 1.32) | Modest absolute gain; depends on clinicians acting; US health system | PMID 33958795 |
| Wearables for AF (meta-analysis) | Smartwatch sens 93%, spec 94% | Accuracy in curated studies ≠ population yield | PMID 32921618 |
| CHW-led BP programs (COBRA-BPS) | −5.2 mmHg vs usual care at 24 mo | Requires sustained workforce time and supervision | PMID 32074419 |

## Trustworthy AI considerations
- WHO "Ethics and governance of artificial intelligence for health" (2021): "the product of eighteen months of deliberation"; AI technologies "must put ethics and human rights at the heart of its design, deployment, and use"; identifies "six consensus principles". URL: https://www.who.int/publications/i/item/9789240029200
- Multinational survey of hospital patients' attitudes to AI in health care (JAMA Netw Open 2025, PMID 40493367) — title-level only; results not extracted.

## Gaps / blocked
- Thai digital health platforms (Mor Prom, H4U, Smart อสม.), Thai FDA SaMD regulation, PDPA health-data rules, smartphone penetration among Thai elderly: NOT VERIFIED (web search engines blocked by bot challenges; PubMed hits irrelevant).
- Thai AI-ECG / retinal CV-risk projects at Siriraj/Ramathibodi: not searched successfully.

## Sources
1. https://pubmed.ncbi.nlm.nih.gov/41766720/ National trends IHD among hypertensives Thailand 2011–2018 (Glob Heart 2026)
2. https://pubmed.ncbi.nlm.nih.gov/42212245/ DSMES cluster RCT Thailand (Lancet Reg Health SE Asia 2026)
3. https://pubmed.ncbi.nlm.nih.gov/42375857/ Health literacy cluster RCT, NE Thailand (Belitung Nurs J 2026)
4. https://pubmed.ncbi.nlm.nih.gov/42820082/ Chatbot HTN program older adults (J Multidiscip Healthc 2026)
5. https://pubmed.ncbi.nlm.nih.gov/40840931/ Digitalizing Emergency Referral System, N. Thailand (Healthc Inform Res 2025)
6. https://pubmed.ncbi.nlm.nih.gov/31530479/ Lao thrombolysis under Thai teleconsultation (2019)
7. https://pubmed.ncbi.nlm.nih.gov/31722151/ Perez. Apple Heart Study (NEJM 2019)
8. https://pubmed.ncbi.nlm.nih.gov/33958795/ Yao. EAGLE AI-ECG RCT (Nat Med 2021)
9. https://pubmed.ncbi.nlm.nih.gov/32921618/ Wearables AF diagnostic accuracy meta-analysis (2021)
10. https://pubmed.ncbi.nlm.nih.gov/32074419/ Jafar. COBRA-BPS (NEJM 2020)
11. https://www.who.int/publications/i/item/9789240029200 WHO Ethics & governance of AI for health (2021)
12. https://pubmed.ncbi.nlm.nih.gov/40493367/ Multinational attitudes toward AI in health care (JAMA Netw Open 2025)
