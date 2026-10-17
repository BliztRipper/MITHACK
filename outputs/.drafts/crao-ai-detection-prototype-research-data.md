# T3: Datasets, pretrained models, and capture hardware for an enhanced CRAO fundus-AI prototype

Brief: `outputs/.plans/crao-ai-detection-prototype-T3.md`. Date: 2026-10-17.
Base paper: Gungor, Sarbout et al., JAHA 2025, doi 10.1161/JAHA.124.041441 (PMID 40576025, PMC12449985). Local full text: `CRAO-AI-detection.md`.

Status per question: Q1 **done**, with ODIR total and MuReD licence unverified. Q2 **done**, with FIVES class list and papilledema licence unverified. Q3 **done**: VisionFM per-disease results and compute were not read. Q4 **done**, with Thai-specific evidence a gap. Q5 **done**.

## Search terms used
- web (exa/openai): "JSIEC 1000 fundus images 39 categories Kaggle CRAO BRAO count"; "RFMiD 2.0 dataset CRAO BRAO labels counts license"; "ODIR-5K dataset license retinal artery occlusion"; "MuReD multi-label retinal disease dataset 2022 BRAO CRAO count"; "EyeQ fundus image quality assessment dataset EyePACS 28792"; "public fundus photograph dataset papilledema optic disc swelling NAION download"; "central retinal artery occlusion deep learning fundus photographs github code dataset"; "retinal artery occlusion fundus images public dataset download deep learning 2024"; "Gungor Sarbout CRAO deep learning fundus code availability"; "handheld fundus camera versus tabletop image quality emergency department Optomed Aurora"; "smartphone fundus photography emergency department FOTO-ED"; "D-EYE smartphone ophthalmoscope ... retinal artery occlusion"; "D-EYE official store price"; "Optomed Aurora price USD"; "Remidio FOP NM-10 price Thailand".
- Europe PMC REST: `RFMiD AND (CRAO OR "artery occlusion")`; `Pachade RFMiD`; `AUTH:"Yoo TK" AND "artery occlusion"`; `"central retinal artery occlusion" AND ("deep learning" OR "artificial intelligence") AND fundus AND PUB_YEAR:[2023 TO 2026]`; `(Thailand OR Thai) AND (handheld OR smartphone OR portable) AND fundus`.
- Direct APIs: Kaggle dataset API (`linchundan/fundusimage1000`), Zenodo API (RFMiD, AIROGS), figshare API (FIVES), Mendeley Data public API (MuReD, RAO dataset), Hugging Face model API (RETFound, VisionFM, RetiZero, FLAIR, EyeCLIP), GitHub API (repo licences/READMEs; search "retinal artery occlusion", "CRAO fundus"), PubMed E-utilities (PMIDs 40163243, 42598096, 42676972), PhysioNet (BRSET).
- **Counted locally:** I downloaded the RFMiD 2.0 zip from Zenodo and counted labels in its 3 CSVs. I downloaded the Mendeley RAO zip (sha256 `84a5fac2…2e9b`, matches the API) and counted files per folder. I read the RFMiD 1.0 PDF from mdpi-res.com, Table 3.
- alphaXiv / `alpha_*` tools were **not used**. The tool was not exposed in this subagent, and an arXiv API call for FLAIR (2308.07898) timed out.

## Evidence table

| # | Source | URL | Key claim | Type | Confidence |
|---|---|---|---|---|---|
| 1 | Gungor et al., JAHA 2025 (base paper, local full text + Europe PMC XML) | https://doi.org/10.1161/JAHA.124.041441 | Public training data = AIROGS 305 normal + "Kaggle" 38 normal/66 CRVO/16 CRAO; data "available ... upon reasonable request"; custom CNN; no code statement | primary | high |
| 2 | JSIEC 1000-image subset, Kaggle API + openmedlab card | https://www.kaggle.com/datasets/linchundan/fundusimage1000 | 1,000 imgs / 39 classes; RAO 16, CRVO 22, BRVO 44, disc swelling 13, normal 38; licence tag ODbL/DbCL but "copyright ... belongs to JSIEC" | primary (dataset) | high |
| 3 | Cen et al., Nat Commun 2021 | https://www.nature.com/articles/s41467-021-25138-w | Full JSIEC-based set 249,620 imgs; non-EyePACS data only on request | primary | high |
| 4 | RFMiD 1.0, Pachade et al., Data 2021 6(2):14 | https://mdpi-res.com/d_attachment/data/data-06-00014/article_deploy/data-06-00014.pdf | 3,200 imgs, 46 conditions, CC-BY 4.0; CRAO 4, BRAO 4, CRVO 45, BRVO 119, ODE 96, AION 26, normal 669 | primary | high |
| 5 | RFMiD 2.0, Zenodo 7505822 (CSV counted locally) | https://zenodo.org/records/7505822 | 860 imgs, CC-BY 4.0; CRAO 1, no BRAO column, CRVO 12, BRVO 22, ODE 20, AION 4, WNL 262 | primary (dataset) | high |
| 6 | RIADD/RFMiD challenge model card, Zenodo 7786002 | https://zenodo.org/records/7786002 | Challenge used 28 classes + OTHER; no CRAO/BRAO class | secondary | medium |
| 7 | MuReD, Rodríguez et al., arXiv 2207.02335v3; Mendeley 10.17632/pc4mb3h8hz.1 | https://arxiv.org/html/2207.02335v3 | 2,208 imgs / 20 labels (ARIA+STARE+RFMiD-train); NORMAL 493, CRVO 55, BRVO 79, ODE 57; no RAO class | primary | high |
| 8 | RAO fundus photography dataset, Yoo TK, Mendeley v2 (2024-11-11) | https://data.mendeley.com/datasets/5428684j44 | CC BY 4.0; zip = 127 web-crawled + 16 JSIEC + 8 RFMiD RAO images (counted locally); no normal class | primary (dataset) | high |
| 9 | Ryu, Choi, Yoo, Med Biol Eng Comput 2025 (PMID 40163243) | https://doi.org/10.1007/s11517-025-03353-7 | SimCLR-pretrained ResNet50 RAO detector; external AUC 0.924 and 0.988; web-based public data | primary (abstract only) | medium |
| 10 | nwuAI/RAONet GitHub | https://github.com/nwuAI/RAONet | RETFound + ResNet fusion for Normal/BRAO/incomplete/subtotal/total CRAO; CFP+OCT; weights on Baidu; licence CC BY-NC 4.0 | primary (repo) | medium |
| 11 | EyeQ, Fu et al., GitHub HzFu/EyeQ | https://github.com/HzFu/EyeQ | 28,792 EyePACS imgs: Good 16,817 / Usable 6,435 / Reject 5,540; code CC BY-NC-SA 4.0; MCF-Net weights "no longer usable" | primary (repo) | high |
| 12 | Rotterdam EyePACS AIROGS train set, Zenodo 5793241 | https://zenodo.org/records/5793241 | 101,442 CFP / 54,274 subjects / ~500 sites; CC BY-NC-ND 4.0 | primary (dataset) | high |
| 13 | FIVES, figshare 19688169 (Jin et al., Sci Data 2022) | https://figshare.com/articles/figure/FIVES_A_Fundus_Image_Dataset_for_AI-based_Vessel_Segmentation/19688169 | 800 CFP, CC BY 4.0, vessel segmentation, "multi-disease" | primary (dataset) | high |
| 14 | Papilledema dataset (Kim U), openmedlab card → OSF 2w5ce | https://github.com/openmedlab/Awesome-Medical-Dataset/blob/main/resources/Papilledema.md | normal 779, papilledema 295, pseudopapilledema 295 (1,369); licence unknown | secondary | medium |
| 15 | BRSET, PhysioNet v1.0.1 | https://physionet.org/content/brazilian-ophthalmological/1.0.1/ | 16,266 imgs / 8,524 pts; label "vascular_occlusion" (artery/vein not split); credentialed DUA | primary (dataset page) | high |
| 16 | EDDFS GitHub | https://github.com/xia-xx-cv/EDDFS_dataset | 28,877 imgs, 15,000 healthy, RVO class, no RAO class; non-commercial only | primary (repo) | medium |
| 17 | RETFound GitHub rmaphoh/RETFound | https://github.com/rmaphoh/RETFound | Licence CC BY-NC 4.0; HF weights gated (form); ~300M ViT-L; train.sh batch 24, 50 epochs, input 224; finetune or lp | primary (repo) | high |
| 18 | Zhou et al., RETFound, Nature 2023 | https://www.nature.com/articles/s41586-023-06555-x | 904,170 CFP + 736,442 OCT; fine-tune batch 16, 50 ep, lr 5e-4 cosine; T4 ~70 min per 1,000 imgs; ischaemic stroke AUROC 0.754; no RAO/RVO eval | primary | high |
| 19 | VisionFM GitHub ABILab-CUHK/VisionFM | https://github.com/ABILab-CUHK/VisionFM | CC BY-NC 4.0; per-modality weights (Fundus, OCT, FFA, …) on Google Drive; fine-tune code | primary (repo) | high |
| 20 | Wang et al., RetiZero, Nat Commun 2025 16:5528 | https://www.nature.com/articles/s41467-025-60577-9 | 341,896 image-text pairs, >400 diseases; RAO singled out for gains (numbers in suppl.); "not intended for commercial purposes" | primary | high |
| 21 | RetiZero GitHub LooKing9218/RetiZero | https://github.com/LooKing9218/RetiZero | Weights via Google Drive; no licence file | primary (repo) | high |
| 22 | FLAIR GitHub jusiro/FLAIR + HF jusiro2/FLAIR | https://github.com/jusiro/FLAIR | Code and weights Apache-2.0; HF not gated; zero-shot text prompts; pretraining includes RFMiD and JSIEC 1000x39 | primary (repo) | high |
| 23 | Aurora vs Nidek AFC-230, J Clin Med 2022 11:2352 (PMC9103652) | https://pmc.ncbi.nlm.nih.gov/articles/PMC9103652/ | Handheld 50° vs tabletop 45°; ungradable eyes 1.42% vs 1.89%; any-DR sens 96.9% / spec 94.8% (dilated) | primary | high |
| 24 | NMFP in the ER review, Curr Neurol Neurosci Rep 2025 (PMC11991934) | https://pmc.ncbi.nlm.nih.gov/articles/PMC11991934/ | FOTO-ED: EP sens 46% / spec 96% with NMFP vs 0% with ophthalmoscope; 13 acute CRAO in 385 ED pts; handheld expert sens 85% / spec 91%; NMFP 45% vs smartphone 40% | secondary | medium-high |
| 25 | Smartphone fundus imaging review, Diagnostics 2024 14:1395 (PMC11240943) | https://pmc.ncbi.nlm.nih.gov/articles/PMC11240943/ | Tabletop cameras "upwards of USD 10,000"; some smartphone setups "below USD 1000"; smartphone 50%/94% vs nonmyd camera 81%/94% (Ryan 2015) | secondary | medium |
| 26 | Akella et al., Front Neurol 2026 (PMID 42598096) | https://pubmed.ncbi.nlm.nih.gov/42598096/ | 100 CRAO/BRAO in ED with NMFP-OCT; 16% <4.5 h; diagnosed by OCT only in 19/100; 3/100 uninterpretable | primary (abstract) | high |
| 27 | Wang et al., Ophthalmol Sci 2026 (PMID 42676972) | https://doi.org/10.1016/j.xops.2026.101338 | Review: ED fundus imaging + AI; portable nonmydriatic devices broaden access | secondary (abstract) | medium |
| 28 | Optomed US store (search snippet; page fetch blocked) | https://www.optomed.com/us/product/optomed-aurora-retinal-set | Aurora IQ retinal set US$8,595; full set US$8,895 | vendor | medium |
| 29 | Remidio shop | https://shop.remidio.com/products/portable-retinal-screening-fop-nm-10 | FOP NM-10 €6,900 sale (€9,900 regular); "AI-enabled workflows" | vendor | high |
| 30 | mHealthSpot 2015 / MobiHealthNews (D-EYE) | https://mhealthspot.com/2015/06/deye-portable-retinal-imaging-system-395-eur/ | D-EYE €395 (2015) / US$435 (MobiHealthNews), out of date | secondary (news) | low |

## Findings

### Q1. Public fundus datasets with retinal artery occlusion (RAO) labels
- **The base paper's "Kaggle" set is the JSIEC 1,000-image subset.** In Table 1 of the base paper, "Kaggle" contributes "38 normal 66 CRVO 16 CRAO". The public sources are cited as refs 34 and 35. Ref 35 is Cen et al., "Automatic detection of 39 fundus diseases…" [1]. The JSIEC subset on Kaggle has RAO 16, CRVO 22, BRVO 44 and normal 38 [2]. Its 16 RAO and 38 normal match the base paper exactly. The paper's 66 "CRVO" equals JSIEC's 22 CRVO + 44 BRVO [1][2]. **Inference:** the base paper probably merged BRVO into its CRVO class, and its 16 public "CRAO" images may include BRAO, because JSIEC labels RAO without a central/branch split [2].
- **JSIEC subset licence is unclear.** The Kaggle API reports "Database: Open Database, Contents: Database Contents" (ODbL/DbCL), yet the description says "The copyright of these images belongs to JSIEC" [2]. It is 447 MB and was last updated 2019-06-18 [2]. The full 249,620-image collection is available only on request [3].
- **RFMiD 1.0:** 3,200 images from 3 cameras (TOPCON 3D OCT-2000, Kowa VX-10α, TOPCON TRC-NW300), 46 conditions, "Dataset License: CC-BY 4.0" [4]. Table 3 lists **CRAO 4, BRAO 4**, CRVO 45, BRVO 119, ODE 96, AION 26, normal 669 [4]. The RIADD challenge built on it uses only 28 classes plus OTHER, and CRAO/BRAO are not among them [6].
- **RFMiD 2.0:** 860 images, 51 diseases, CC-BY 4.0 [5]. In my local count of the label CSVs (train 509 / val 177 / test 174), **CRAO = 1** (in training) and there is **no BRAO column**. Other counts: CRVO 12, BRVO 22, ODE 20, AION 4, WNL (normal) 262. IIH and HTN columns are also present [5].
- **MuReD:** 2,208 images in 20 labels, built from ARIA (143) + STARE (388) + RFMiD training (1,920) [7]. **There is no RAO label.** Rare classes were merged into OTHER (261) [7]. Licence not captured from Mendeley (UNVERIFIED).
- **A dedicated RAO set exists:** "RAO (retinal artery occlusion) fundus photography dataset", by Yoo TK (Hangil Eye Hospital), Mendeley v2, 2024-11-11, CC BY 4.0 [8]. My count of the zip: **127 web-crawled + 16 JSIEC + 8 RFMiD = 151 RAO images**. It has no normal or other classes and no CRAO/BRAO/time-from-onset labels [8]. The companion paper (Ryu, Choi, Yoo 2025) used a SimCLR-pretrained ResNet50 and reported external AUCs of 0.924 and 0.988 [9]. I read only its abstract, so the composition of the external sets is unverified.
- **RAONet repo** (NWU SAIL Lab): RETFound + ResNet fusion on CFP and OCT. Classes are Normal, BRAO, Incomplete/Subtotal/Total CRAO [10]. Trained weights are on Baidu Netdisk and the licence is CC BY-NC 4.0 [10]. The training dataset and results were not found in the README.
- **ODIR-5K:** "central retinal artery occlusion" appears as a diagnostic keyword in the ODIR training keyword histogram (count 1 in one class row, PMC10002549 Table A1; https://pmc.ncbi.nlm.nih.gov/articles/PMC10002549/). The total RAO count and the licence are **UNVERIFIED**.
- **BRSET** (Brazil): 16,266 images / 8,524 patients. It has a single label, `vascular_occlusion`, with no artery/vein split. Access is credentialed (PhysioNet Credentialed Health Data License 1.5.0 + CITI training) [15].
- **EDDFS:** 28,877 images, of which 15,000 are healthy. It has an RVO class and no RAO class. Use is "for non-commercial research purposes only" with no redistribution [16].
- **No RAO labels:** AIROGS (glaucoma/referable/ungradable) [12] and FIVES (vessel segmentation) [13]. APTOS and Messidor are DR datasets. I did not check their licences because they contain no RAO labels.
- **Bottom line:** across all open sources there are about **151 unique RAO images**. That count assumes the Mendeley set already includes the JSIEC 16 and RFMiD 8; RFMiD 2.0 adds 1 [2][4][5][8]. None is labelled hyperacute (<4.5 h).

### Q2. Differential classes (CRVO, NAION/disc oedema, normal) and image quality
- **CRVO:** JSIEC 22 (+44 BRVO) [2]; RFMiD 1.0 45 (+119 BRVO) [4]; RFMiD 2.0 12 (+22 BRVO) [5]; MuReD 55 (+79 BRVO), overlapping with RFMiD [7]; EDDFS has RVO (count not read) [16].
- **NAION / disc oedema:** RFMiD 1.0 has AION 26 and ODE 96 [4]; RFMiD 2.0 has AION 4, ODE 20 and an IIH column [5]; JSIEC has "Disc swelling and elevation" 13 [2]; MuReD has ODE 57 [7]. The Papilledema dataset (Kim U, OSF) has papilledema 295, pseudopapilledema 295 and normal 779. Its licence is unknown because OSF returned 503 [14]. **No public set found labels NAION specifically.** AION/ODE are the closest proxies.
- **Normal:** AIROGS train has 101,442 images (CC BY-NC-ND 4.0, of which the base paper used 305) [12][1]. Also RFMiD 1.0 normal 669 [4], RFMiD 2.0 WNL 262 [5], MuReD 493 [7], JSIEC 38 [2], EDDFS 15,000 [16].
- **Image quality:** EyeQ has 28,792 EyePACS images graded Good 16,817 / Usable 6,435 / Reject 5,540, split train 12,543 / test 16,249 [11]. The code is CC BY-NC-SA 4.0, and the label CSVs are in the repo. The original MCF-Net weights are "no longer usable", so the model must be retrained [11]. AIROGS also includes an "ungradable" label [12].

### Q3. Pretrained retinal models
- **RETFound** [17][18]:
  - Code is CC BY-NC 4.0 [17].
  - Hugging Face weights `YukunZhou/RETFound_mae_natureCFP`, `_mae_natureOCT`, `_mae_meh`, `_mae_shanghai`, `_dinov2_meh` and `_dinov2_shanghai` are gated (you must request access through a form). Each is a ~300M-parameter ViT-L [17].
  - Setup: ImageFolder layout `train/val/test/<class>/`, `sh train.sh` → `torchrun main_finetune.py --batch_size 24 --epochs 50 --input_size 224 --adaptation finetune|lp`. The README also points to a free-GPU Colab notebook [17].
  - Paper recipe: batch 16, 50 epochs (10 warm-up), lr 5e-4 cosine annealed to 1e-6, with label smoothing [18].
  - Compute: fine-tuning on one **NVIDIA T4 (16 GB) takes "about 70 min for every 1,000 images"**. The Discussion gives "about 1.2 h" for the same 1,000 images [18].
  - Pretraining used 904,170 CFP + 736,442 OCT [18].
  - Data efficiency: it beat the comparison models with 10% of the labels for heart failure / MI [18].
  - Stroke: ischaemic-stroke prediction AUROC 0.754 internally [18]. There is no RAO/RVO evaluation [18].
- **VisionFM** [19]: CC BY-NC 4.0. Separate weights per modality (Fundus, OCT, FFA, …) on Google Drive, with fine-tuning code released 2024/05. Example single-class decoder training uses `--batch_size_per_gpu 32` [19]. I did not read the paper's per-disease results or compute needs.
- **RetiZero** [20][21]: a vision-language model pretrained on 341,896 image-text pairs covering more than 400 diseases [20].
  - The paper names RAO among the diseases with notable gains, both internally and cross-domain. The figures are in Supplementary Figs. 12–14, which I did not read [20].
  - EYE-52 zero-shot top-1/3/5 is 0.360/0.626/0.756, versus FLAIR's 0.092/0.263/0.340 [20].
  - 5-shot AUCs on common-disease sets are 0.967/0.859/0.942 [20].
  - Weights are on Google Drive and the repo has no licence file [21]. The paper says it is "sorely for academic research and is not intended for commercial purposes" [20].
- **FLAIR** [22]: code and weights are **Apache-2.0**. Hugging Face `jusiro2/FLAIR` is not gated (safetensors), and `FLAIRModel.from_pretrained("jusiro2/FLAIR")` gives zero-shot scores from text prompts. Linear-probe and few-shot runs use `main_transferability.py --shots_train`. Its pretraining data include RFMiD and JSIEC 1000x39 [22].
- **Other Hugging Face checkpoints found:** `bitfount/RETFound_MAE`, `bitfount/RETFound_MAE_OCT`, `YukunZhou/RETFound_dinov2_*`, `ronnief1/RetFiner-VisionFM`. Their cards and licences were not read.
- **No few-shot results specifically for CRAO** were found for RETFound, VisionFM or FLAIR. RetiZero's RAO results exist only in its supplement [20].

### Q4. Capture hardware
- **Handheld vs tabletop** (Padova, 213 diabetic patients / 423 eyes, dilated) [23]:
  - Optomed Aurora: 50°, 2368×1776 px, minimum pupil 3.1 mm. Nidek AFC-230: 45°, 3744×3744 px, minimum pupil 4 mm.
  - Eyes with at least one ungradable image: 1.42% (Aurora) vs 1.89% (Nidek).
  - Aurora for any DR: sensitivity 96.9%, specificity 94.8%. For referable DR: 100% / 99.8% [23].
- **ED evidence** [24]:
  - FOTO-ED: emergency physicians reading nonmydriatic photos reached 46% sensitivity / 96% specificity, versus 0% sensitivity with the direct ophthalmoscope.
  - Biousse ED series: 385 patients, including 13 acute CRAO.
  - Systematic review: handheld cameras read by experts reached 85% sensitivity / 91% specificity.
  - FUNDUS study: handheld NMFP 45% vs smartphone 40% sensitivity.
  - The Remidio NM-10 is named in the review [24].
- **NMFP + OCT in the ED** (Akella et al., 2026): 100 CRAO/BRAO eyes [26].
  - Only 16% presented within 4.5 h.
  - Diagnosis came from colour photos + OCT in 77/100, from **OCT only in 19/100**, and imaging was uninterpretable in 3/100.
  - 7 of the 16 early eyes received IV thrombolysis [26].
- **Smartphones** [25]: smartphone imaging typically trails desktop cameras (Ryan 2015: 50% / 94% vs 81% / 94%). Some setups cost "below USD 1000", and tabletop cameras cost "upwards of USD 10,000" [25].
- **Prices:**
  - Optomed Aurora IQ retinal set: US$8,595, full set US$8,895, from a search-result snippet of the Optomed US store; the page fetch was blocked [28].
  - Remidio FOP NM-10: €6,900 sale / €9,900 regular [29].
  - D-EYE: €395 / US$435 in 2015 news. Current official pricing is UNVERIFIED [30].
  - Thai prices and distributors: UNVERIFIED.

### Q5. Is the base paper's model, code or data public?
- Data: "available from the corresponding author upon reasonable request" [1]. The text has no code-availability statement and no GitHub link for the model [1]. The only GitHub link, ref 41 (Classif-Eye), is the "semiautomated image annotation application" the neurologists used for grading, not the model [1].
- Architecture: a custom CNN (strided + classic convolutions, ReLU, fully connected layers, SoftMax) with hyperparameters set by grid search. No pretrained backbone is named [1]. GitHub searches ("retinal artery occlusion", "CRAO fundus") found no reimplementation.
- **Not public:** model, weights and code. Only the 425 public training images (AIROGS 305 + JSIEC 120) can be rebuilt [1][2][12].

## Implications for the enhanced version and prototype (inference)
- **Easy prototype, ~24 h:**
  - Model: FLAIR (Apache-2.0, ungated) for zero-shot, then a linear probe [22]. Alternatively RETFound-CFP with `--adaptation lp`, then fine-tuning, on a free T4/Colab at ~70 min per 1,000 images [17][18].
  - Data, 4 classes:
    - RAO: Mendeley RAO set, 151 images [8].
    - CRVO: RFMiD 1.0 CRVO + JSIEC CRVO, keeping BRVO separate or as a 5th class [2][4].
    - Disc oedema (NAION proxy): RFMiD ODE/AION + JSIEC disc swelling [2][4].
    - Normal: AIROGS / RFMiD [4][12].
  - Add an EyeQ-trained quality gate in front of the classifier [11].
- **Leakage risk:** FLAIR and RetiZero pretrained on RFMiD and JSIEC [20][22], and the Mendeley RAO set reuses JSIEC/RFMiD images [8]. Zero-shot scores on those images will look better than they are. Hold out the web-crawled subset and report results by source.
- **Main ceiling on claims:** no public image is labelled hyperacute (<4.5 h) [1][8]. A public-data prototype can show "RAO vs mimics" triage but cannot replicate the 0.96 hyperacute AUC. Say so explicitly in the pitch.
- **Enhancement directions backed by evidence:**
  - Add OCT: it was decisive in 19% of ED cases [26], and RETFound has OCT weights [17].
  - Add a handheld-camera pathway: Aurora gradability is comparable to tabletop [23], at roughly US$8.6k vs >US$10k for tabletop [25][28].
  - Add telestroke-style remote reading [26].
- **Licensing for a deployable product:** RETFound, VisionFM, RAONet, AIROGS, EyeQ and EDDFS are all non-commercial [10][11][12][16][17][19], and RetiZero is academic-only [20]. FLAIR (Apache-2.0) and the CC BY datasets (RFMiD, FIVES, Mendeley RAO) are the commercially safer stack [4][5][8][13][22]. Even so, the Mendeley set's web-crawled and JSIEC content may carry third-party rights [2][8].

## Conflicts and gaps
- **CRVO count conflict:** the base paper's 66 "CRVO" from Kaggle equals JSIEC CRVO 22 + BRVO 44 [1][2]. The 16 "CRAO" are JSIEC's combined RAO class and may include BRAO.
- **JSIEC licence conflict:** Kaggle tags it ODbL/DbCL, but the description says JSIEC holds the copyright [2].
- **RETFound fine-tune time:** the paper gives both "70 min per 1,000 images" and "1.2 h with 1,000 images" [18]. The paper also uses batch 16 while the README's train.sh uses batch 24 [17][18].
- **Optomed price:** the official US store lists US$8,595 [28], while reseller snippets list US$3,990–4,400 (protech-medical.com, maxamedical.com). Reseller prices are UNVERIFIED and may be for a different configuration.
- **Gaps:**
  - MuReD licence, Papilledema dataset licence and ODIR RAO total are unverified.
  - RetiZero's RAO numbers are in the supplement, which I did not read.
  - The Yoo 2025 external test sets were not read (abstract only) [9].
  - RAONet's dataset and results were not found [10].
  - I found no Thai data on handheld fundus cameras or their prices.
  - VisionFM per-disease results were not read.
  - FIVES class list was not verified.
  - alphaXiv was not used.

## Sources
1. Gungor A, Sarbout I, et al. Artificial Intelligence-Based Detection of Central Retinal Artery Occlusion Within 4.5 Hours on Standard Fundus Photographs. J Am Heart Assoc. 2025 — https://doi.org/10.1161/JAHA.124.041441 (PMC12449985)
2. JSIEC "1000 Fundus images with 39 categories" (Kaggle, linchundan; 2019) — https://www.kaggle.com/datasets/linchundan/fundusimage1000 ; card: https://github.com/openmedlab/Awesome-Medical-Dataset/blob/main/resources/JSIEC.md
3. Cen L-P et al. Automatic detection of 39 fundus diseases and conditions in retinal photographs using deep neural networks. Nat Commun. 2021 — https://www.nature.com/articles/s41467-021-25138-w
4. Pachade S et al. Retinal Fundus Multi-Disease Image Dataset (RFMiD). Data. 2021;6(2):14 — https://mdpi-res.com/d_attachment/data/data-06-00014/article_deploy/data-06-00014.pdf
5. RFMiD 2.0 (Zenodo, 2023) — https://zenodo.org/records/7505822
6. RIADD/RFMiD trained model card (Zenodo, 2023) — https://zenodo.org/records/7786002
7. Rodríguez MA et al. Multi-Label Retinal Disease Classification using Transformers (MuReD). arXiv 2207.02335 (2022) — https://arxiv.org/html/2207.02335v3 ; data https://data.mendeley.com/datasets/pc4mb3h8hz/1
8. Yoo TK. RAO (retinal artery occlusion) fundus photography dataset, v2 (Mendeley Data, 2024) — https://data.mendeley.com/datasets/5428684j44
9. Ryu SY, Choi JY, Yoo TK. Automated detection of retinal artery occlusion in fundus photography via self-supervised deep learning… Med Biol Eng Comput. 2025 — https://doi.org/10.1007/s11517-025-03353-7
10. nwuAI/RAONet (GitHub) — https://github.com/nwuAI/RAONet
11. Fu H et al. EyeQ (GitHub) — https://github.com/HzFu/EyeQ
12. de Vente C et al. Rotterdam EyePACS AIROGS train set (Zenodo, 2021) — https://zenodo.org/records/5793241
13. Jin K et al. FIVES (figshare, 2022) — https://figshare.com/articles/figure/FIVES_A_Fundus_Image_Dataset_for_AI-based_Vessel_Segmentation/19688169
14. Papilledema dataset card (openmedlab) → OSF — https://github.com/openmedlab/Awesome-Medical-Dataset/blob/main/resources/Papilledema.md ; https://osf.io/2w5ce/
15. BRSET, Brazilian Multilabel Ophthalmological Dataset (PhysioNet v1.0.1) — https://physionet.org/content/brazilian-ophthalmological/1.0.1/
16. Xia X et al. EDDFS dataset (GitHub) — https://github.com/xia-xx-cv/EDDFS_dataset
17. RETFound (GitHub, rmaphoh) — https://github.com/rmaphoh/RETFound ; weights https://huggingface.co/YukunZhou/RETFound_mae_natureCFP
18. Zhou Y et al. A foundation model for generalizable disease detection from retinal images. Nature. 2023 — https://www.nature.com/articles/s41586-023-06555-x
19. VisionFM (GitHub, ABILab-CUHK) — https://github.com/ABILab-CUHK/VisionFM
20. Wang M et al. Enhancing diagnostic accuracy in rare and common fundus diseases with a knowledge-rich vision-language model (RetiZero). Nat Commun. 2025;16:5528 — https://www.nature.com/articles/s41467-025-60577-9
21. RetiZero (GitHub) — https://github.com/LooKing9218/RetiZero
22. Silva-Rodríguez J et al. FLAIR (GitHub; HF jusiro2/FLAIR) — https://github.com/jusiro/FLAIR ; https://huggingface.co/jusiro2/FLAIR
23. Handheld Fundus Camera for DR Screening: comparison with table-top camera. J Clin Med. 2022;11:2352 — https://pmc.ncbi.nlm.nih.gov/articles/PMC9103652/
24. The Use of Fundus Photography in the Emergency Room — A Review. Curr Neurol Neurosci Rep. 2025 — https://pmc.ncbi.nlm.nih.gov/articles/PMC11991934/
25. Clinical Applications and Future Directions of Smartphone Fundus Imaging. Diagnostics. 2024;14:1395 — https://pmc.ncbi.nlm.nih.gov/articles/PMC11240943/
26. Akella M et al. Impact of an eye-stroke protocol with non-mydriatic ocular imaging in an emergency department. Front Neurol. 2026 — https://pubmed.ncbi.nlm.nih.gov/42598096/
27. Wang Y et al. The Underutilized Ocular Fundus in Emergency Departments… Ophthalmol Sci. 2026 — https://doi.org/10.1016/j.xops.2026.101338
28. Optomed Aurora IQ retinal set (Optomed US store) — https://www.optomed.com/us/product/optomed-aurora-retinal-set
29. Remidio FOP NM-10 (Remidio shop) — https://shop.remidio.com/products/portable-retinal-screening-fop-nm-10
30. D-EYE now available for 395 EUR (mHealthSpot, 2015) — https://mhealthspot.com/2015/06/deye-portable-retinal-imaging-system-395-eur/

## Coverage status
- **Checked directly:**
  - Base-paper text.
  - Dataset counts for JSIEC (card), RFMiD 1.0 (PDF table), RFMiD 2.0 (CSV), MuReD (paper table), Mendeley RAO (zip listing), EyeQ, AIROGS and FIVES (repository metadata).
  - Licences via GitHub, Zenodo, figshare, Mendeley and Hugging Face APIs.
  - RETFound and RetiZero papers (answer-mode extraction).
  - Hardware studies (answer-mode extraction).
  - PubMed abstracts.
- **Uncertain or not done:** see "Conflicts and gaps". alphaXiv tools were unavailable in this run. MDPI pages returned 403; the RFMiD 1.0 PDF was obtained from the mdpi-res.com CDN instead. OSF and PMC JavaScript pages failed.
