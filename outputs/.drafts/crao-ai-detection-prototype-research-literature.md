# T1: AI literature on CRAO / retinal artery occlusion, for the enhanced prototype

Brief: `outputs/.plans/crao-ai-detection-prototype-T1.md`. Compiled 2026-10-17.
Base paper [1]: Gungor, Sarbout et al., JAHA 2025, doi 10.1161/JAHA.124.041441. Facts about it come from the local full text `CRAO-AI-detection.md`.

Question status: Q1 done · Q2 done · Q3 done (no CRAO-specific handheld, smartphone or UWF-camera AI study found) · Q4 done (no RAO-specific foundation-model numbers found in the text I read) · Q5 done · Q6 done (only one multimodal CRAO-AI paper found, and I read only its abstract) · Q7 done.

## Search terms used
- PubMed (E-utilities, 2026-10-17):
  - `("retinal artery occlusion"[tiab] OR CRAO[tiab] OR BRAO[tiab]) AND (deep learning OR artificial intelligence OR machine learning OR neural network OR foundation model OR GPT OR large language model)` (26 hits)
  - `("retinal artery occlusion" OR "artery occlusion") AND (fundus OR ultra-widefield OR fluorescein) AND (deep learning OR convolutional OR AI)` (19 hits)
  - multi-disease fundus + RAO (5 hits)
  - `"central retinal artery occlusion" AND OCT AND (fundus OR cherry red) AND (hyperacute OR 4.5 OR early OR onset OR sensitivity)` (31 hits)
  - `(GPT-4V OR GPT-4o OR Gemini OR MLLM OR vision-language OR ChatGPT OR Claude OR LLM) AND (fundus OR retinal image OR retina)` (139 hits; I screened every abstract for RAO)
  - `(RAO OR monocular vision loss OR amaurosis fugax OR acute vision loss) AND (triage OR algorithm OR decision support OR prediction model OR telemedicine OR telestroke OR machine learning)` (72 hits)
- OpenAlex: `retinal artery occlusion deep learning` (from 2018 on); a forward-citation list for the base paper (W4411710523, 14 citing works).
- alphaXiv (`feynman alpha search -m both`): "retinal foundation model rare disease few-shot retinal artery occlusion"; "vision language model fundus photograph diagnosis GPT-4V Gemini evaluation"; "retinal artery occlusion deep learning fundus". I pulled the text of 2406.09317, 2308.07898, 2512.14499, 2606.22955 and 2310.04992.
- Web (Exa) queries:
  - DL + RAO + fundus + external validation
  - UWF + RAO
  - "39 fundus diseases"
  - OCT + DL + acute CRAO hyperreflectivity
  - FOTO-ED + BONSAI
  - smartphone/handheld + ED + RAO
  - handheld vs tabletop DL
  - "Do Machines Dream of Cherry Red Spots"
  - VisionFM
  - multimodal fundus + clinical stroke triage
  - EyeCLIP + RAO
- Full text read via Europe PMC XML: PMC8355164 (Cen 2021), PMC11634984 (Beuse 2025), PMC10550819 (RETFound), PMC11009408 (OCTDL).

## Evidence table

| # | Source | URL | Key claim | Type | Confidence |
|---|---|---|---|---|---|
| 1 | Gungor, Sarbout et al., JAHA 2025 (base paper) | https://doi.org/10.1161/JAHA.124.041441 | Hyperacute (<4.5 h) CRAO: AUC 0.96, sens 92.6%, spec 85.0%. 54 hyperacute test photos. Beat 3 stroke neurologists | primary | high |
| 2 | Ryu, Choi, Yoo, Med Biol Eng Comput 2025 | https://doi.org/10.1007/s11517-025-03353-7 | SimCLR-pretrained ResNet50 on RAO fundus photos. External AUC 0.924 and 0.988. GPT-4 chatbot plus Grad-CAM explanations | primary (abstract) | medium |
| 3 | Yoo, Mendeley Data RAO fundus dataset v2, 2024 | https://data.mendeley.com/datasets/5428684j44 | CC BY 4.0. One 65.9 MB zip. Built from web images plus RFMiD and JSIEC | dataset metadata | high |
| 4 | Cen et al., Nat Commun 2021 (39 diseases) | https://doi.org/10.1038/s41467-021-25138-w | RAO bigclass: multihospital external sens 0.933, spec 1.000, AUC 0.9999 | primary | high |
| 5 | Duan & Tu, Front Cell Dev Biol 2025 (UWF) | https://doi.org/10.3389/fcell.2025.1630667 | UWF, 16 classes. Only 18 RAO images, 3 in the external test | primary | medium |
| 6 | Lam J et al., ARVO 2025 abstract "Do Machines Dream of Cherry Red Spots" | https://iovs.arvojournals.org/article.aspx?articleid=2804831 | AI on CRAO fundus photos. Page blocked (403); title and authors only | abstract | low |
| 7 | Beuse et al., Ophthalmol Sci 2025 (OCT DL) | https://doi.org/10.1016/j.xops.2024.100630 | ResNet-18 on OCT. 50 CRAO. CRAO-class AUC 0.99, sens 0.96, spec 0.97. Mean onset to assessment 13.2 h | primary | high |
| 8 | Wenzel et al., Front Med 2022 | https://doi.org/10.3389/fmed.2022.854288 | Inner-retina OCT hyperreflectivity AUC 0.99. Visible at 1–4 h after onset | primary | medium-high |
| 9 | Walter et al., Front Neurol 2026 | https://doi.org/10.3389/fneur.2026.1783055 | Reflectivity and thickness on OCT separate <4.5 h from ≥4.5 h (AUC 0.88–0.93). n=39 | primary | medium |
| 10 | Balal et al., Curr Eye Res 2021 | https://doi.org/10.1080/02713683.2021.1921219 | 11 of 214 CRAO first missed. All had inner-retinal ischaemia on the first OCT | primary | medium |
| 11 | Zhou, Chen, Zou, Xiao, Inf Fusion 2024 | https://doi.org/10.1016/j.inffus.2023.102200 | Uncertainty-weighted fusion of incomplete multimodal data for few-shot CRAO classification. Mean accuracy 90.31% | primary (abstract) | low-medium |
| 12 | Kulyabin et al., OCTDL, Sci Data 2024 | https://doi.org/10.1038/s41597-024-03182-7 | Open OCT dataset of 2,064 B-scans. Only 22 RAO scans from 11 patients | dataset | high |
| 13 | WaveAttention-ResNet, Front Radiol 2025 | https://doi.org/10.3389/fradi.2025.1608052 | OCTDL 7-class model (includes RAO): acc 90.68%, AUC 97.50% | primary (abstract) | medium |
| 14 | Akella … Biousse, Front Neurol 2026 | https://doi.org/10.3389/fneur.2026.1885492 | 100 acute CRAO/BRAO in the ED. 19 of 100 diagnosed from OCT only. 16% presented <4.5 h | primary | high |
| 15 | Bénard-Séguin … Biousse, J Stroke Cerebrovasc Dis 2024 | https://doi.org/10.1016/j.jstrokecerebrovasdis.2024.107895 | Hyperacute fundus "may appear 'normal'". OCT helps. 26 RAO in year 1 | primary | high |
| 16 | Gilbert … Vora, Am J Ophthalmol Case Rep 2024 | https://doi.org/10.1016/j.ajoc.2024.102204 | Kaiser telemedicine fundus-photo pathway. 85 naCRAO <4.5 h, 35 given TNK | primary | medium |
| 17 | Dumitrascu … Demaerschalk, Telemed J E Health 2023 | https://doi.org/10.1089/tmj.2022.0286 | Mayo telestroke: 5 possible CRAO, 4 within 4.5 h, none thrombolysed | primary | medium |
| 18 | Biousse … Newman (BONSAI), Am J Ophthalmol 2024 | https://doi.org/10.1016/j.ajo.2023.10.025 | DL on non-mydriatic FOTO-ED photos: papilledema AUC 0.97. 1,608 photos | primary | high |
| 19 | Gungor … Milea (BONSAI), J Neuroophthalmol 2026 | https://doi.org/10.1097/WNO.0000000000002394 | DL trained on mydriatic photos, tested on handheld Optomed Aurora: papilledema AUC 98.3%, sens 81.0% | primary | high |
| 20 | He et al., Curr Eye Res 2023 | https://doi.org/10.1080/02713683.2023.2215984 | Desktop vs portable camera agreement varies by disease: DR κ 0.80, AMD κ 0.41, GON κ 0.32 | primary | high |
| 21 | Optomed CRAO page | https://www.optomed.com/us/offer/crao | Vendor claim that handheld images can confirm or exclude CRAO. No CRAO AI data | vendor / self-reported | low |
| 22 | Stroke 2025 abstract TP172 | https://doi.org/10.1161/str.56.suppl_1.tp172 | Fundus cameras in 10 stroke-certified EDs for CRAO/BRAO. Content blocked (406) | abstract | low |
| 23 | Zhou et al., RETFound, Nature 2023 | https://doi.org/10.1038/s41586-023-06555-x | 1.6 M images. No RAO-specific result; JSIEC multiclass AUROC averaged across classes | primary | high |
| 24 | Wang et al., RetiZero, arXiv 2406.09317 | https://arxiv.org/abs/2406.09317 | More than 400 diseases. Zero-shot Top-5 0.756 on 52 diseases. Text names RAO as a strong class; no number in the text I read | preprint | medium |
| 25 | Silva-Rodríguez et al., FLAIR, arXiv 2308.07898 | https://arxiv.org/abs/2308.07898 | Pretraining includes RFMiD and JSIEC, which carry CRAO/BRAO labels. No RAO evaluation found | preprint | medium |
| 26 | Guo et al., ReVision, arXiv 2512.14499 | https://arxiv.org/abs/2512.14499 | 485,980 photo–report pairs. Zero-shot mean AUROC 0.946. CRAO/BRAO among labels; no CRAO AUROC found | preprint | medium |
| 27 | Xia et al., Evo-RAD, arXiv 2606.22955 | https://arxiv.org/abs/2606.22955 | Agentic retrieval for rare retinal disease. No RAO mention in the text I read | preprint | low |
| 28 | Qiu et al., VisionFM, arXiv 2310.04992 (NEJM AI 2024) | https://arxiv.org/abs/2310.04992 | Multimodal ophthalmic foundation model. No RAO mention in the alphaXiv text I read | preprint | low |
| 29 | Gupta & Al-Kazwini, Cureus 2024 | https://doi.org/10.7759/cureus.73660 | ChatGPT-4 got 4 of 12 fundus diagnoses right and failed CRAO. "often hallucinates" | primary (tiny n) | medium |
| 30 | Huo et al., Retina 2026 | https://doi.org/10.1097/IAE.0000000000004986 | 800 fundus photos: GPT-4o 75%, Claude 3.5 Sonnet 18%, Grok-2 18%, Gemini 1.5 14% | primary | medium-high |
| 31 | Front Med 2026, "Comparative performance of contemporary multimodal LLMs in retinal imaging QA" | https://doi.org/10.3389/fmed.2026.1934968 | 6 multimodal LLMs on OCTCases questions: 59.3–77.4% accuracy | primary | medium |
| 32 | Wang Y … Wong TY, Zhu Z, Ophthalmol Sci 2026 (review) | https://doi.org/10.1016/j.xops.2026.101338 | Fundus AI in the ED still needs validation | review | medium |
| 33 | "Updates in CRAO", J Neuroophthalmol 2026 (review) | https://doi.org/10.1097/WNO.0000000000002440 | IVT <4.5 h has the strongest evidence. Eye-stroke protocols with AI improved diagnostic efficiency | review | medium |
| 34 | Hoyek … Patel, Am J Ophthalmol 2025 | https://doi.org/10.1016/j.ajo.2024.10.004 | 145 CRAO eyes; only 19% examined within 4.5 h | primary | high |
| 35 | Berman … Biousse, Surv Ophthalmol 2025 | https://doi.org/10.1016/j.survophthal.2024.09.012 | Method for putting a non-mydriatic camera in an ED. Metadata only | review | low |
| 36 | OpenAlex works citing the base paper | https://api.openalex.org/works?filter=cites:W4411710523 | 14 citing works; all are reviews or adjacent studies, none a new CRAO-AI primary study | index | medium |

## Findings

### Q1. Other AI for CRAO, BRAO or RAO on colour fundus photos (2018–2026)
- **Base paper [1].**
  - Training set: 1,039 photos from 517 patients.
  - Hyperacute test set: 54 CRAO photos from 54 patients. It "misclassif[ied] only 4 out of 54", which is 92.6% sensitivity. AUC was 0.96.
  - A second test set covered CRAO within 24 h: 110 photos from 109 patients.
  - The reader comparison against neurologists used "a subset of hyperacute testing data set (120 photographs, 120 patients)", which includes the non-CRAO classes.
  - Data: "available from the corresponding author upon reasonable request". No public code was found in the text.
- **Ryu, Choi & Yoo 2025 [2].**
  - Self-supervised SimCLR pretraining, then a ResNet50 classifier for RAO.
  - "AUC of 0.924 and 0.988 on two external validation datasets." The paper says it uses "publicly accessible, de-identified, web-based data".
  - It pairs Grad-CAM with a ChatGPT-4 chatbot that produces explanations, for example of retinal whitening and the cherry-red spot.
  - The abstract describes it as "the first application of deep learning for this purpose". That conflicts with [4], which reported RAO results in 2021.
  - Its dataset appears to be the public Mendeley set [3]. That is an inference from the same author and the same "web-based public data" wording.
  - No onset-time stratification. I read the abstract only.
- **Cen et al. 2021 [4]: a 39-class system.** It is a two-level hierarchy of CNNs plus Mask-RCNN, trained on 249,620 images. RAO is one class; CRAO and BRAO are not separated.
  - Primary test (27,611 images, all classes): RAO sens 0.950, spec 1.000, AUC 1.0000.
  - Multihospital external test (60,445 images, 3 Chinese sites): sens 0.933, spec 1.000, AUC 0.9999.
  - Comparative set (922 images): DL sens 1.000 vs average expert 0.929.
  - The number of RAO images and the time since onset are not in the main-text tables. I infer that the cases were mostly non-hyperacute.
  - Data: JSIEC (1,000 images, 39 classes) is public; the rest is available on request.
- **Ultra-widefield (UWF), Duan & Tu 2025 [5].** DenseNet121 features fed to XGBoost, 16 classes, 10,612 UWF images.
  - RAO had only 18 images in total. Validation recall was 0.75. The external AUC of 1.000 rests on 3 images, so it is not informative.
- **ARVO 2025 abstract by Lam et al. [6].** It evaluates AI on CRAO fundus photos. The page was blocked, so I have no results. UNVERIFIED.
- **Summary.** I found no other study besides [1] that reports performance stratified by time since CRAO onset, or a hyperacute subgroup, on fundus photos.
  - The near-perfect RAO numbers in [4] and [5] come from mixed or late-stage RAO inside large multi-disease systems. They are not comparable with the <4.5 h task in [1].

### Q2. OCT-based AI for acute CRAO, and OCT vs fundus at the hyperacute stage
- **Beuse et al. 2025 [7], Tübingen and Hamburg.**
  - ResNet-18 on Spectralis B-scans.
  - 155 individuals and 293 scans: 50 CRAO patients, 34 differential-diagnosis scans (CRVO, DME, NAION), and controls (50 fellow eyes plus 159 others).
  - Results: CRAO sens 0.96, spec 0.97, AUC 0.99. Control AUC 0.96. Differential AUC 0.90.
  - "The average estimated time between the onset of CRAO … and clinic assessment was 13.2 hours." No <4.5 h subgroup was reported.
  - CAVEAT: the paper calls itself an "external validation study", but the method is nested 5-fold cross-validation on pooled data from the two centres.
  - The authors list the "relatively small size of the data set" and "only high-quality imaging" as limitations.
- **OCT biomarkers without deep learning.**
  - Wenzel 2022 [8]: 56 CRAO within 48 h.
    - Inner-retinal optical intensity was 177 ± 19 in CRAO eyes vs 123 ± 14 in fellow eyes.
    - A cut-off of 149.46 gave AUC 0.99 and sens 0.93.
    - The increase was "already visible in patients with a very short time since symptom onset (1–4 h)". The authors caveat the "relatively low number of patients within the first 3 h".
  - Walter 2026 [9]: 39 CRAO (12 under 4.5 h).
    - The IRL/ORL ratio distinguishes CRAO from the fellow eye (AUC 0.98).
    - Reflectivity and thickness ratios distinguish <4.5 h from ≥4.5 h: IRL/ORL AUC 0.88; RRTI S9 AUC 0.93.
    - These are threshold analyses, not AI. They are relevant to estimating onset time from imaging.
- **OCT vs fundus, sensitivity at the hyperacute stage.**
  - There is no head-to-head diagnostic-accuracy study in hyperacute CRAO in what I read. The indirect evidence follows.
  - In 100 ED cases with both photos and OCT [14], the diagnosis came from photos plus OCT in 77, OCT only in 19, and imaging was uninterpretable in 3. This is not split by onset time.
  - [15]: "In the hyper-acute setting, the ocular fundus may appear 'normal' … but is facilitated by retinal optical coherence tomography (OCT)."
  - [8]: "funduscopic changes, such as a cherry red spot or retinal pallor, may be lacking within the IVT-relevant very early phase, while ischemic signs may already become apparent on [OCT]".
  - [10]: 11 of 214 CRAO (5.14%) were first misdiagnosed. "All cases had evidence of inner retinal ischaemia" on the first OCT.
  - The base paper itself calls OCT "a more sensitive modality for detecting acute CRAO" [1].
- **Public OCT data with RAO.**
  - OCTDL [12] has 22 RAO B-scans from 11 patients, out of 2,064 scans, taken on an Optovue Avanti. The article is CC BY 4.0; I did not check the dataset's own licence.
  - Models trained on OCTDL include a ResNet50 baseline (7-class AUC 0.988) [12] and WaveAttention-ResNet (acc 90.68%, AUC 97.50%) [13].
  - Per-class RAO numbers are not given in either abstract.

### Q3. Ultra-widefield, handheld and smartphone fundus AI, and ED cameras
- **No CRAO-specific AI on handheld, smartphone or UWF cameras.** I found no peer-reviewed study of this, apart from the tiny UWF RAO subset in [5]. The base paper lists this as future work [1].
- **Nearest evidence: BONSAI, from the same group as the base paper.**
  - FOTO-ED non-mydriatic ED photos [18]: 1,608 photos from 828 patients. Normal vs abnormal disc: AUC 0.92, sens 75.6%, spec 89.6%. Papilledema: AUC 0.97, sens 84.0%, spec 98.9%.
  - Handheld camera [19], Optomed Aurora, prospective: 1,552 photos from 817 patients.
    - The model was trained on 18,981 mydriatic photos only.
    - Papilledema: accuracy 99.5%, sens 81.0% (95% CI 64.1–97.7), spec 99.7%, AUC 98.3%.
  - These are optic-disc tasks, not retinal-whitening tasks.
- **Cross-camera transfer depends on the disease.** Paired photos from a desktop Topcon and a portable Optain [20]: 906 pairs from 504 patients, with 59 low-quality photos excluded.
  - Agreement: referable DR κ 0.80, AMD κ 0.41, glaucomatous optic neuropathy κ 0.32.
  - It is unknown how RAO would behave.
- **ED workflows that use non-mydriatic photos and OCT, without AI.**
  - Emory Eye-Stroke protocol [14][15]:
    - 100 consecutive acute CRAO/BRAO cases from 2023 to 2026.
    - Only 16% arrived within 4.5 h. 7 of those 16 received IVT, with a median door-to-needle time of 58 min.
    - Median time from ED arrival to imaging was 28.5 min for patients presenting within 4.5 h.
    - 18% (17/94) had concurrent cerebral infarcts on MRI.
  - Kaiser telemedicine fundus-photo pathway [16]:
    - 85 naCRAO within 4.5 h; 35 got tenecteplase 0.25 mg/kg.
    - VA improvement ≥0.3 logMAR: 54.3% vs 28% (p=.014). Retrospective.
  - Mayo telestroke [17]:
    - Acute ocular complaints were 49 of 9,511 encounters.
    - 5 possible CRAO, 4 of them within 4.5 h, none thrombolysed.
  - TP172 [22]: fundus cameras in 10 stroke-certified EDs. Content blocked.
- **Vendor material.** Optomed's CRAO page [21] claims handheld images are "reliable for confirmation or exclusion of … CRAO". It cites no CRAO study and gives no AI performance data. Treat it as marketing.

### Q4. Retinal foundation models and RAO / few-shot rare disease
- **RETFound [23].**
  - Masked-autoencoder ViT trained on 904,170 fundus photos and 736,442 OCT scans.
  - Fine-tuned on JSIEC's 39 classes, which include CRAO. Multiclass AUROC is "average[d]" across classes.
  - The full text contains no "artery" or "occlusion". So **no RAO-specific result is reported.**
  - Code: github.com/rmaphoh/RETFound_MAE.
- **RetiZero [24], arXiv 2406.09317v3.**
  - 341,896 image–text pairs covering more than 400 diseases.
  - Zero-shot Top-5 accuracy: 0.843 on 15 diseases, 0.756 on 52 diseases. Top-3 zero-shot beat the mean of 19 ophthalmologists.
  - A five-images-per-disease fine-tuning task exists.
  - The text calls the gains "particularly apparent for … retinal artery occlusion". Per-class numbers are in Extended Data Figs 12–14, which I did not read. RAO-specific numbers: UNVERIFIED.
- **FLAIR [25].** Its pretraining data includes RFMiD (with CRAO and BRAO labels) and JSIEC (with CRAO). I found no RAO evaluation in the pages I read. Code: github.com/jusiro/FLAIR.
- **ReVision [26].**
  - 485,980 photos with reports, from a telemedicine programme across 162 Chinese institutions.
  - Zero-shot AUROC 0.946 averaged over 12 public benchmarks.
  - CRAO and BRAO appear among its label categories and in its reader-study differential.
  - I found no CRAO AUROC in the 7 pages of text I retrieved.
- **No RAO mention in the text I retrieved:** VisionFM [28] and Evo-RAD [27]. Evo-RAD is a rare-disease retrieval agent; code at github.com/SDH-Lab/Evo-RAD.
- **Net result.** No foundation model in this set publishes a hyperacute-CRAO or RAO-specific benchmark. Few-shot claims exist only at the level of overall disease sets.

### Q5. Vision-language models and LLMs on fundus diagnosis
- **ChatGPT-4 [29].** 12 textbook fundus images: 4 correct, 1 partly correct. It failed on CRAO. "The model often hallucinates when unsure."
- **Four multimodal LLMs [30].** 800 photos, 8 conditions; the abstract does not list which conditions.
  - Accuracy: GPT-4o 75%, Claude 3.5 Sonnet 18%, Grok-2 18%, Gemini 1.5 14%.
  - Inter-model κ was 0.05–0.16.
- **2026-generation models [31].** On OCTCases multiple-choice questions, accuracy ranged from 59.3% to 77.4% (best: ChatGPT-5.5 Thinking).
- **No CRAO-specific evaluation.** Of 139 PubMed records on LLMs/VLMs and fundus images, only [2] and [29] mention RAO in the abstract.
  - [2] uses GPT-4 only to *explain* a CNN's output, not to make the diagnosis.
- **Med-PaLM M.** I did not check whether it covers fundus images; this remains UNVERIFIED.

### Q6. Multimodal models combining image and clinical context
- **One multimodal CRAO-AI paper [11].** Zhou, Chen, Zou & Xiao (Inf Fusion 2024) classify CRAO from incomplete multimodal data.
  - Method: multi-task classification plus lesion segmentation, and a text-similarity auxiliary loss.
  - Fusion: modality features are weighted by predictive uncertainty.
  - Result: "mean accuracy of 90.31%" on a self-collected dataset.
  - The abstract does not name the modalities or say whether clinical variables are used. Full text was blocked (403).
- **No model fusing photos with onset time, RAPD or symptoms.** I found none for CRAO.
  - Clinical context today enters through human protocols: Eye-Stroke [14][15], Kaiser telemedicine [16], telestroke [17].
  - The ED review [32] and the CRAO update [33] say AI and LLMs are promising but unvalidated in ED practice.

### Q7. Gaps in the base paper: what later work addresses and what is still open
| Gap in [1] | Addressed by later or other work? | Status |
|---|---|---|
| Training CRAO photos were 24 h–30 d after onset; hyperacute test n=54 | No hyperacute training set exists anywhere. Only 16–19% of CRAO present within 4.5 h [14][34] | open |
| Every test CRAO had an abnormal fundus, so normal-fundus hyperacute CRAO may be missed | OCT finds ischaemia when the fundus looks normal [8][10][15]; 19% of ED cases were diagnosed from OCT alone [14] | partly addressed (OCT, not AI on photos) |
| No OCT | OCT DL [7] (not hyperacute-specific, n=50); OCT onset-staging biomarkers [9]; OCTDL has 22 RAO scans [12] | partly |
| Standard cameras only | Same group's DL transferred to a handheld Optomed for papilledema [19]; cross-camera transfer varies by disease [20]; UWF RAO n=18 [5] | open for CRAO |
| Poor-quality and multi-pathology images excluded | No CRAO-specific quality gating found (T4 covers quality gating) | open |
| Retrospective; data on request; no public code | Prospective ED cohorts exist without AI [14][16]; the public RAO dataset [3] is web-sourced | open |
| 4-class closed set (CRAO, CRVO, NAION, normal) | Multi-disease systems include RAO [4][24][26], but without onset-time stratification | partly |
| No clinical context (onset time, RAPD, VA) | Only [11] does multimodal fusion, modalities unknown; no image + clinical CRAO model found | open |
| Single model; no LLM | LLMs are unreliable at reading fundus photos [29][30]; an LLM used only to explain outputs [2] | open (risk) |
| No forward-citing CRAO-AI primary study (14 citing works) [36] | — | open |

## Implications for the enhanced version and prototype (INFERENCE, not source claims)
1. **Use the LLM to orchestrate, not to read images.**
   - Multimodal LLMs scored 14–75% on fundus diagnosis [30] and failed on CRAO [29].
   - So the image call should come from a CNN or foundation-model classifier. The LLM or agent should handle onset-time intake, checklists, escalation and explanation (the pattern in [2]).
2. **Make onset time and "normal fundus does not rule out CRAO" explicit triage rules.** A negative photo result within 4.5 h should send the patient to OCT or specialist review, not to discharge [8][10][14][15].
3. **The quickest data path is public, but it is not hyperacute.**
   - Candidates: Mendeley RAO set (CC BY 4.0) [3], JSIEC [4], RFMiD [25]; OCTDL for an optional OCT branch [12].
   - Any accuracy shown will measure *established* RAO, not hyperacute CRAO. Say this on stage.
   - Licences and image counts are T3's job to confirm.
4. **A foundation-model backbone helps with few-shot RAO,** fine-tuned with a linear probe or small head; candidates are RETFound [23] and RetiZero [24]. No published RAO baseline exists, so the team would produce the first number. Report it with confidence intervals and warn about small n.
5. **Show device robustness.** Even a simple augmentation or test on a different camera answers the base paper's "handheld/wide-angle" limitation. [19][20] show transfer can work but is not guaranteed.
6. **Thailand framing (inference).** The 16%-within-4.5 h figure [14] and failures due to inter-facility transfer suggest the value is in remote first-contact triage over a telestroke network, not in replacing ophthalmologists.

## Conflicts and gaps
- **"First" claim.** [2] calls itself "the first application of deep learning" for RAO on fundus photos. [4] reported RAO results in 2021. Both are noted; neither is preferred.
- **"External validation" label.** [7] uses it for pooled 5-fold cross-validation.
- **Single vs multicentre.** [9] says "multicenter" in the design and "single-center" in its limitations.
- **Near-perfect RAO AUCs ([4] ≈1.0, [5] 1.000).** They come from late or mixed-stage RAO, large class-imbalanced test sets, or very few positives. Do not compare them with the hyperacute AUC of 0.96 in [1].
- **Base paper test-set counts.** 54 hyperacute CRAO photos vs a 120-photo reader subset. These are consistent (the 120 include other classes), but check before quoting.
- **UNVERIFIED or blocked:** [6] ARVO abstract (403); [22] TP172 (406); [11] full text (403); the BONSAI AJO full text (403, abstract used); RetiZero per-class RAO numbers; ReVision CRAO metrics; Med-PaLM M on fundus; the RAO image count in [3].
- **Not found despite searching:** smartphone-camera CRAO AI; a hyperacute fundus-vs-OCT sensitivity study; an image + clinical-variable CRAO model; prospective CRAO AI.

## Coverage status
- Read directly as full text or tables: [1] (local file), [4], [7], [12], [23].
- Read via answer-mode page fetch: [5], [8], [9], [21].
- Read via alphaXiv text: [24], [25], [26], [27], [28], partial pages only.
- Abstract only: [2], [10], [11], [13], [14]–[20], [29]–[35].
- Metadata via API: [3], [36].
- Title only: [6], [22].
- I did not download any datasets.

## Sources
1. Gungor A, Sarbout I, et al. AI-Based Detection of CRAO Within 4.5 Hours on Standard Fundus Photographs. J Am Heart Assoc 2025. https://doi.org/10.1161/JAHA.124.041441 (PMID 40576025; medRxiv https://doi.org/10.1101/2024.12.19.24319390)
2. Ryu SY, Choi JY, Yoo TK. Automated detection of RAO in fundus photography via self-supervised deep learning… Med Biol Eng Comput 2025;63:2679-2691. https://doi.org/10.1007/s11517-025-03353-7 (PMID 40163243)
3. Yoo TK. RAO (retinal artery occlusion) fundus photography dataset, v2, Mendeley Data 2024. https://doi.org/10.17632/5428684j44.2
4. Cen LP, et al. Automatic detection of 39 fundus diseases and conditions… Nat Commun 2021;12:4828. https://doi.org/10.1038/s41467-021-25138-w (PMC8355164)
5. Duan M-M, Tu X. Deep learning-based classification of multiple fundus diseases using ultra-widefield images. Front Cell Dev Biol 2025;13:1630667. https://doi.org/10.3389/fcell.2025.1630667
6. Lam J, Reddy A, et al. Do Machines Dream of Cherry Red Spots… IOVS 2025 (ARVO abstract). https://iovs.arvojournals.org/article.aspx?articleid=2804831
7. Beuse A, et al. Automated Detection of CRAO Using OCT Imaging via Explainable Deep Learning. Ophthalmol Sci 2025;5:100630. https://doi.org/10.1016/j.xops.2024.100630 (PMC11634984)
8. Wenzel DA, et al. Inner Retinal Layer Hyperreflectivity Is an Early Biomarker for Acute CRAO. Front Med 2022;9:854288. https://doi.org/10.3389/fmed.2022.854288
9. Walter A, et al. Retinal layer reflectivity and thickness as OCT biomarkers… relative to the 4.5-h window in acute CRAO. Front Neurol 2026;17:1783055. https://doi.org/10.3389/fneur.2026.1783055
10. Balal S, et al. Capturing the Occult CRAO Using OCT. Curr Eye Res 2021;46:1762-1767. https://doi.org/10.1080/02713683.2021.1921219 (PMID 33882770)
11. Zhou Q, Chen T, Zou H, Xiao X. Uncertainty-aware incomplete multimodal fusion for few-shot CRAO classification. Inf Fusion 2024;104:102200. https://doi.org/10.1016/j.inffus.2023.102200
12. Kulyabin M, et al. OCTDL: OCT Dataset for Image-Based Deep Learning Methods. Sci Data 2024;11:365. https://doi.org/10.1038/s41597-024-03182-7 (PMC11009408)
13. WaveAttention-ResNet… multiple retinal diseases. Front Radiol 2025;5:1608052. https://doi.org/10.3389/fradi.2025.1608052 (PMID 40800169)
14. Akella M, et al. Impact of an eye-stroke protocol with non-mydriatic ocular imaging in an ED. Front Neurol 2026;17:1885492. https://doi.org/10.3389/fneur.2026.1885492 (PMID 42598096)
15. Bénard-Séguin É, et al. Eye stroke protocol in the emergency department. J Stroke Cerebrovasc Dis 2024;33:107895. https://doi.org/10.1016/j.jstrokecerebrovasdis.2024.107895 (PMID 39079617)
16. Gilbert AL, et al. A telemedicine-enabled IV thrombolytic pathway for hyperacute naCRAO. Am J Ophthalmol Case Rep 2024;36:102204. https://doi.org/10.1016/j.ajoc.2024.102204 (PMID 39512749)
17. Dumitrascu OM, et al. Telemedicine for Acute Monocular Visual Loss: Mayo Telestroke Network. Telemed J E Health 2023;29:1738-1743. https://doi.org/10.1089/tmj.2022.0286 (PMID 36912816)
18. Biousse V, et al. Application of a DL System to Detect Papilledema on Nonmydriatic Fundus Photographs in an ED. Am J Ophthalmol 2024;261:199-207. https://doi.org/10.1016/j.ajo.2023.10.025 (PMID 37926337)
19. Gungor A, et al. DL-Based Detection of Papilledema on Retinal Photographs From Handheld Cameras. J Neuroophthalmol 2026;46:98-104. https://doi.org/10.1097/WNO.0000000000002394 (PMID 40867029)
20. He S, et al. Cross-camera Performance of DL Algorithms… Portable Fundus Camera. Curr Eye Res 2023;48:857-863. https://doi.org/10.1080/02713683.2023.2215984 (PMID 37246918)
21. Optomed. Using Mobile Fundus Cameras to Detect/Refute CRAO in EDs (vendor page). https://www.optomed.com/us/offer/crao
22. Implementation of Fundus Cameras in 10 Stroke Certified EDs for Emergent Detection of CRAO/BRAO. Stroke 2025;56(Suppl 1):TP172. https://doi.org/10.1161/str.56.suppl_1.tp172
23. Zhou Y, et al. A foundation model for generalizable disease detection from retinal images (RETFound). Nature 2023. https://doi.org/10.1038/s41586-023-06555-x (PMC10550819)
24. Wang M, et al. Enhancing Diagnostic Accuracy in Rare and Common Fundus Diseases with a Knowledge-Rich Vision-Language Model (RetiZero). arXiv 2406.09317. https://arxiv.org/abs/2406.09317
25. Silva-Rodríguez J, et al. A Foundation Language-Image Model of the Retina (FLAIR). arXiv 2308.07898. https://arxiv.org/abs/2308.07898
26. Guo J, Du J, et al. Native Intelligence Emerges from Large-Scale Clinical Practice: A Retinal Foundation Model… (ReVision). arXiv 2512.14499. https://arxiv.org/abs/2512.14499
27. Xia W, Du Y, et al. Evo-RAD: Rare Retinal Disease Diagnosis via Self-Evolving Agentic Retrieval. arXiv 2606.22955. https://arxiv.org/abs/2606.22955
28. Qiu J, et al. VisionFM: a Multi-Modal Multi-Task Vision Foundation Model for Generalist Ophthalmic AI. arXiv 2310.04992. https://arxiv.org/abs/2310.04992 (NEJM AI https://doi.org/10.1056/AIoa2300221)
29. Gupta A, Al-Kazwini H. Evaluating ChatGPT's Diagnostic Accuracy in Detecting Fundus Images. Cureus 2024;16:e73660. https://doi.org/10.7759/cureus.73660
30. Huo L, et al. Diagnostic Accuracy of Multimodal LLMs in Retinal Fundus Photography. Retina 2026. https://doi.org/10.1097/IAE.0000000000004986 (PMID 42640646)
31. Comparative performance of contemporary multimodal LLMs in retinal imaging question answering. Front Med 2026;13:1934968. https://doi.org/10.3389/fmed.2026.1934968 (PMID 42694118)
32. Wang Y, et al. The Underutilized Ocular Fundus in EDs: Imaging and AI. Ophthalmol Sci 2026;6:101338. https://doi.org/10.1016/j.xops.2026.101338
33. Updates in Central Retinal Artery Occlusion. J Neuroophthalmol 2026;46:1-7. https://doi.org/10.1097/WNO.0000000000002440 (PMID 41700954)
34. Hoyek S, et al. Multimodal Imaging Characteristics… CRAO Presenting to a Large Academic Center. Am J Ophthalmol 2025;270:35-51. https://doi.org/10.1016/j.ajo.2024.10.004
35. Berman G, et al. Breaking the barriers: implementation of a non-mydriatic fundus camera in an ED. Surv Ophthalmol 2025;70:153-161. https://doi.org/10.1016/j.survophthal.2024.09.012
36. OpenAlex, works citing W4411710523 (base paper), queried 2026-10-17. https://api.openalex.org/works?filter=cites:W4411710523
