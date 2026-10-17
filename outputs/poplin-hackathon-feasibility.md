# Feasibility: Building a Hackathon Prototype on Poplin et al. 2018

*Deep-research report, 2026-10-17. Siriraj x MIT Hackathon, Cardiovascular Diseases track.*

## Question

Paper: Poplin et al. 2018, Nature Biomedical Engineering, "Prediction of cardiovascular risk factors from retinal fundus photographs via deep learning" (https://www.nature.com/articles/s41551-018-0195-0). Context: Siriraj x MIT Hackathon, Cardiovascular Diseases track in Thailand (lead problem is uncontrolled hypertension). Question: is it valid and feasible to build on this paper and make a simple prototype within a hackathon timeframe (about 24-48h, small team, consumer GPU or Colab)? Cover: (1) whether the paper's findings held up (replications, external validation, especially in Asian or Thai populations, and follow-ups such as RETFound, Reti-CVD, SIVA-DLS, Rim et al. 2021 Lancet Digital Health); (2) open datasets and pretrained weights available for retina-to-CVD-risk or blood pressure prediction (UK Biobank access limits, EyePACS, RETFound weights, and so on) and their licences; (3) realistic prototype scope, such as fine-tuning RETFound on public data versus a demo with saliency maps, and what accuracy to expect (the paper reports SBP MAE about 11 mmHg and MACE AUC 0.70); (4) clinical, regulatory, and ethical caveats for pitching it in Thailand (Thai FDA SaMD, PDPA); (5) concrete ways to enhance the original work that suit a hackathon.

## Summary

Yes, building on Poplin et al. 2018 is valid for a hackathon prototype, provided it is pitched as a research demo and not as a diagnostic tool. Independent work supports the core idea that retinal photos carry signal about cardiovascular risk. A 2024 replication on UK Biobank matched Poplin's systolic blood pressure (SBP) error at about 11 mmHg (R2 about 0.39). In a Kenyan cohort, a UK Biobank-trained model kept a hypertension AUC of about 0.77 but had slightly worse error. In Asian cohorts (Korea and Singapore), follow-up models RetiCAC, Reti-CVD and SIVA-DLS predicted cardiovascular events with modest discrimination (AUC or C-index about 0.71-0.75; hazard ratios about 1.3-2.0). None of these was a Thai cohort, and none tested Poplin's own model. The main thing limiting a 24-48 hour build is data, not compute. The open fundus datasets the research found have no blood pressure readings or cardiovascular outcomes (BRSET, for example, also needs PhysioNet credentialing that takes days). UK Biobank cannot realistically be accessed within a hackathon. RETFound weights are gated on HuggingFace, licensed non-commercial (CC BY-NC 4.0), and come with a Colab notebook and a single-GPU fine-tuning script, which makes them a practical backbone if the team requests access before the event. A realistic scope is a hypertension-focused demo: a RETFound or ImageNet backbone fine-tuned on a public proxy label (for example hypertensive retinopathy, age or sex), shown with saliency maps and an honest panel of benchmarks from the literature. The team should not claim Poplin-level SBP or MACE accuracy unless it actually has blood pressure-labelled data. Thai FDA software-as-a-medical-device (SaMD) rules and PDPA (Thailand's data protection law) were not covered by any verified evidence and need separate checking.

## Findings

### 1. Poplin-level SBP prediction can be reproduced with a standard model. A fine-tuned ImageNet Inception-v3 on UK Biobank reached SBP MAE 11.0 mmHg and R2 0.39 (averaging both eyes), against a mean-only baseline MAE of 14.4 mmHg and Poplin's R2 of 0.36. Age prediction was strong (R2 0.81, MAE 2.77 years). HbA1c (R2 0.058) and total cholesterol (R2 0.016) were barely predictable, so a prototype should not be built on retina-derived lab values.

- **Confidence:** medium
- **Vote:** 3-0 (both merged claims)
- **Sources:** <https://arxiv.org/pdf/2410.11535>
- **Evidence:** University of Amsterdam master's thesis on arXiv (not peer-reviewed), with an internal 60/20/20 split of UK Biobank and no external test. Training only the last layers gave much weaker results (age R2 0.52), which is closer to what a hackathon compute budget would deliver. The thesis notes that earlier work found SBP R2 fell to about 0.16 on external sets.

### 2. A UK Biobank-trained retinal model generalised moderately to a non-European population. In Kenya (n=301), the hypertension AUC was 0.765, versus 0.738 in UK Biobank. SBP/DBP mean absolute error was comparable or slightly worse (about 12.3 vs 11.4 mmHg for SBP). Only 49% of SBP predictions fell within 10 mmHg.

- **Confidence:** medium
- **Vote:** 3-0 (both merged claims)
- **Sources:** <https://dom-pubs.onlinelibrary.wiley.com/doi/10.1111/dom.15587?af=R>
- **Evidence:** White et al., Diabetes Obes Metab 2024, a prospective peer-reviewed study (only the abstract was reachable). The small cohort gives wide confidence intervals, and higher hypertension prevalence may raise the AUC. A separate claim that the authors called for population-specific recalibration was refuted 0-3 as worded, although the abstract does say recalibration 'may be appropriate'. The cohort is African, not Asian or Thai.

### 3. The retina-to-cardiovascular-risk approach held up in Asian populations, with modest effect sizes. RetiCAC, trained in Korea, predicted coronary artery calcium with AUC 0.742. Its risk groups were linked to fatal cardiovascular events in a 10-year Singapore cohort (n=8551, HR trend 1.33, 95% CI 1.04-1.71) and in UK Biobank (HR 1.28). In a Korean clinical cohort (n=527, 33 events) it reached C-index 0.71, comparable to CT-based CAC scoring.

- **Confidence:** high
- **Vote:** 3-0 (three merged claims)
- **Sources:** <https://www.thelancet.com/journals/landig/article/PIIS2589-7500(21)00043-1/fulltext>
- **Evidence:** Rim et al., Lancet Digit Health 2021, peer-reviewed primary source checked through the abstract on Europe PMC and Mediwhale's page. This tests a different model with a different target (CAC), not Poplin's model. The Singapore SEED cohort is multi-ethnic Chinese/Malay/Indian, not Thai. The C-index rests on a small number of events and is not directly comparable to Poplin's MACE AUC of 0.70.

### 4. In a mostly hypertensive Korean cohort (CMERC-HI, n=1106, about 93% hypertensive, 33 events over 5 years), Reti-CVD risk groups had an adjusted HR trend of 2.02 (1.26-3.24) for cardiovascular events. Harrell's C-index was 0.751, versus 0.741 for CAC, 0.707 for CIMT and 0.710 for baPWV, and the authors describe it as non-inferior to CAC. This is the evidence closest to the track's uncontrolled-hypertension problem.

- **Confidence:** medium
- **Vote:** 3-0 (two merged claims)
- **Sources:** <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10746299/>
- **Evidence:** Lee et al., JAMIA 2023, peer-reviewed. Caveats: one centre, only 33 events, heavily overlapping confidence intervals, no formal non-inferiority test, a C-index from a model that also includes traditional risk factors, and authors from Mediwhale (the vendor), which is a likely conflict of interest.

### 5. SIVA-DLS measures retinal vessel calibre as an explainable intermediate biomarker. It was developed and validated on more than 70,000 multi-ethnic, mostly Asian images. Its associations with risk factors such as blood pressure were as strong as, or stronger than, those from expert graders. Its baseline measurements were linked to later cardiovascular disease, and in Singaporean Asians with CKD (n=860, 9.3-year follow-up) narrower arterioles independently predicted cardiovascular disease (adjusted HR 1.40 per SD, 1.17-1.68).

- **Confidence:** high
- **Vote:** 3-0 (four merged claims)
- **Sources:** <https://www.nature.com/articles/s41551-020-00626-4>, <https://pmc.ncbi.nlm.nih.gov/articles/PMC10689182/>
- **Evidence:** Cheung et al., Nat Biomed Eng 2021, and Clin Kidney J 2023, both peer-reviewed primary sources. The country list given for the cohorts was partly unverified (New Zealand was not confirmed). These are associations, not individual-level blood pressure accuracy. A claim that SIVA-DLS raised the AUC to 0.760 was refuted 0-3. The CKD paper has a published correction whose content was not checked. A vessel-calibre approach fits a hypertension pitch well because the biomarker can be explained.

### 6. RETFound is a practical backbone for a hackathon with conditions. It is a self-supervised ViT-Large foundation model pretrained on about 1.6M retinal images (about 900k colour fundus photos for the fundus weights) and is designed for label-efficient fine-tuning. The official repo has a Colab notebook, a single-GPU train.sh (batch size 24), and a train/val/test folder-per-class data layout. Six weight sets (MAE: natureCFP, natureOCT, meh, shanghai; DINOv2: meh, shanghai) are hosted on HuggingFace behind a registration and access gate.

- **Confidence:** high
- **Vote:** 3-0 (four merged claims); related 'Colab makes it feasible' claim refuted 1-2
- **Sources:** <https://github.com/rmaphoh/RETFound>, <https://github.com/openmedlab/RETFound_MAE>, <https://huggingface.co/open-eye/RETFound_MAE>
- **Evidence:** Checked on the maintainers' repo and HF model page. The openmedlab mirror is stale and offers Google Drive links to the older weights. The pipeline does classification only, so SBP regression needs a regression head and MSE loss added. ViT-L at batch 24 may not fit a free T4, so the batch size may need lowering. The broader claim that Colab makes it feasible was rejected, so the team should not assume free Colab is enough. Access should be requested before the event.

### 7. RETFound code and weights are licensed CC BY-NC 4.0. That is fine for a hackathon or research prototype, but it bars commercial use, which matters if the prototype is meant to become a startup. A commercial licence would have to be negotiated with the authors (UCL/Moorfields) and is not guaranteed.

- **Confidence:** high
- **Vote:** 3-0 (two merged claims)
- **Sources:** <https://github.com/openmedlab/RETFound_MAE>, <https://huggingface.co/open-eye/RETFound_MAE>, <https://github.com/rmaphoh/RETFound>
- **Evidence:** The LICENSE file text and the HF model card both say CC BY-NC 4.0. Whether a hackathon with an industry sponsor counts as non-commercial is a grey area.

### 8. Open data is the main bottleneck. BRSET (16,266 photos from 8,524 Brazilian patients) has no blood pressure or cardiovascular outcome variables, only age, sex, diabetes fields, free-text comorbidities and an image-level hypertensive retinopathy label. It also requires PhysioNet credentialing, CITI training and a signed DUA, which usually takes days to weeks. It cannot supervise Poplin-style SBP or MACE prediction and is only usable if access is arranged before the event.

- **Confidence:** high
- **Vote:** 3-0 (two claims), 2-1 (size/usability claim)
- **Sources:** <https://physionet.org/content/brazilian-ophthalmological/1.0.2/>, <https://pmc.ncbi.nlm.nih.gov/articles/PMC10854338/>
- **Evidence:** Primary PhysioNet page and data descriptor. Realistic proxy targets are age, sex, diabetes and hypertensive retinopathy. The patients are Brazilian, so it adds no Thai validity. The split vote reflects the dataset being described as 'open' when access is restricted.

### 9. Realistic prototype scope and enhancements (synthesised from the findings above, not separately verified): (a) fine-tune RETFound or Inception-v3 on an accessible proxy label, for example hypertensive retinopathy or age, with a regression head if any blood pressure-labelled data is available; (b) show Grad-CAM/attention saliency over the vessels; (c) add an explainable vessel-calibre and arteriole-narrowing readout in the spirit of SIVA-DLS that ties to hypertension; (d) frame the product as smartphone or low-cost fundus screening that flags uncontrolled hypertension for referral in Thai primary care, combining the retinal score with cuff blood pressure and clinical factors; (e) present literature benchmarks honestly, expecting about 11-12 mmHg SBP MAE at best with blood pressure labels and a cardiovascular-event C-index or AUC around 0.70-0.75, and propose a Thai validation and recalibration study with Siriraj as the next step.

- **Confidence:** medium
- **Vote:** inference
- **Sources:** <https://arxiv.org/pdf/2410.11535>, <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10746299/>, <https://www.nature.com/articles/s41551-020-00626-4>, <https://dom-pubs.onlinelibrary.wiley.com/doi/10.1111/dom.15587?af=R>
- **Evidence:** Drawn from the verified accuracy ranges, the data limits and RETFound's fine-tuning setup. No verified source tested this exact pipeline in 48 hours.

## Caveats

The research question had five parts, and part (4), Thai FDA SaMD classification and PDPA obligations for health and image data, has no verified evidence at all. It needs separate checking before pitching. No verified claim covers Poplin's own model being externally validated, or any Thai or Southeast Asian cohort. All the Asian evidence comes from Korea and Singapore and is for different models (RetiCAC, Reti-CVD, SIVA-DLS). Several Asian studies have vendor-affiliated authors (Mediwhale) and few events (33), so their confidence intervals are wide. The SBP replication is a master's thesis that has not been peer-reviewed. Several publisher pages returned 403, so some checks relied on abstracts only. EyePACS, UK Biobank access timelines, and other datasets with blood pressure labels were not verified. RETFound gating, licence terms and the BRSET version are time-sensitive; they were checked as of October 2026. The claim that free Colab is enough was refuted, so GPU memory remains a practical risk with ViT-Large. The prototype-scope finding is a synthesis, not a verified source.

## Open questions

- Under Thai FDA rules, would a retinal hypertension or cardiovascular-risk screening app count as SaMD, and which risk class? What does PDPA require for collecting or processing Thai fundus images in a pilot?
- Is there any publicly accessible fundus dataset with measured blood pressure or cardiovascular outcomes that a team could use within 48 hours, or could Siriraj provide de-identified data under a hackathon agreement?
- How well do UK-, Korean- or Singapore-trained retinal models perform on Thai patients and on smartphone or low-cost fundus cameras, and how much recalibration would be needed?
- Does RETFound fine-tuning beat a simple ImageNet Inception-v3 or a general foundation model (for example DINOv2) on blood pressure or hypertension proxies, given a hackathon's compute and data limits?

## Refuted claims

- ~~Adding the SIVA-DLS retinal vessel features to established risk factors and eGFR raised the AUC for incident CVD only modestly, from 0.720 (risk factors alone) and 0.743 (with eGFR) to 0.760. This is about the same level as the MACE AUC of 0.70 reported by Poplin et al.~~ (vote 0-3; <https://pmc.ncbi.nlm.nih.gov/articles/PMC10689182/>)
- ~~The authors conclude that models trained on UK Biobank need population-specific recalibration before use in a new population. This bears on reusing UK-trained or Western-trained weights for a Thai population.~~ (vote 0-3; <https://dom-pubs.onlinelibrary.wiley.com/doi/10.1111/dom.15587?af=R>)
- ~~The official repo has a Colab notebook that runs on a free GPU, so fine-tuning in a short hackathon on Colab looks feasible.~~ (vote 1-2; <https://github.com/rmaphoh/RETFound>)

## Sources

| # | URL | Quality | Angle |
|---|---|---|---|
| 1 | <https://www.thelancet.com/journals/landig/article/PIIS2589-7500(21)00043-1/fulltext> | primary | Replication and external validation in Asian populations |
| 2 | <https://www.nature.com/articles/s41551-020-00626-4> | primary | Replication and external validation in Asian populations |
| 3 | <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10746299/> | primary | Replication and external validation in Asian populations |
| 4 | <https://pmc.ncbi.nlm.nih.gov/articles/PMC10689182/> | primary | Replication and external validation in Asian populations |
| 5 | <https://dom-pubs.onlinelibrary.wiley.com/doi/10.1111/dom.15587?af=R> | primary | Replication and external validation in Asian populations |
| 6 | <https://github.com/openmedlab/RETFound_MAE> | primary | Open datasets, pretrained weights, licences |
| 7 | <https://physionet.org/content/brazilian-ophthalmological/1.0.2/> | primary | Open datasets, pretrained weights, licences |
| 8 | <https://www.kaggle.com/datasets/andrewmvd/ocular-disease-recognition-odir5k> | secondary | Open datasets, pretrained weights, licences |
| 9 | <https://github.com/rmaphoh/RETFound> | primary | Practitioner prototype and achievable accuracy |
| 10 | <https://arxiv.org/pdf/2410.11535> | primary | Practitioner prototype and achievable accuracy |
| 11 | <https://huggingface.co/open-eye/RETFound_MAE> | primary | Practitioner prototype and achievable accuracy |
| 12 | <https://pmc.ncbi.nlm.nih.gov/articles/PMC10854338/> | primary | Practitioner prototype and achievable accuracy |
| 13 | <https://www.nature.com/articles/s41598-020-65794-4> | primary | Skeptical limits and confounding |
| 14 | <https://academic.oup.com/ehjdh/advance-article-pdf/doi/10.1093/ehjdh/ztae068/59076482/ztae068.pdf> | secondary | Skeptical limits and confounding |
| 15 | <https://pmc.ncbi.nlm.nih.gov/articles/PMC13412995/> | secondary | Skeptical limits and confounding |
| 16 | <https://www.sciencedirect.com/science/article/abs/pii/S0010482525002926> | primary | Skeptical limits and confounding |
| 17 | <https://pmc.ncbi.nlm.nih.gov/articles/PMC11570365/> | secondary | Skeptical limits and confounding |
| 18 | <https://www.nature.com/articles/s43856-026-01573-y> | primary | Skeptical limits and confounding |
| 19 | <https://www.qualtechs.com/en-gb/article/thai-fda-samd-ai-guidance-2024> | secondary | Thai regulation, ethics, deployment context |
| 20 | <https://asiaactual.com/blog/thailand-issues-guidance-on-samd-registration/> | secondary | Thai regulation, ethics, deployment context |
| 21 | <https://www.tilleke.com/insights/thailand-issues-personal-data-protection-guidelines-for-ai-systems/> | secondary | Thai regulation, ethics, deployment context |
| 22 | <https://pubmed.ncbi.nlm.nih.gov/35272972/> | primary | Thai regulation, ethics, deployment context |

## Method

Search angles: 5. Sources fetched: 22. Claims extracted: 107. Claims verified: 25, of which 22 confirmed and 3 refuted. Each claim got a 3-vote adversarial check (2 of 3 refutes to reject it).
