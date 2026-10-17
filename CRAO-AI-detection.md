---
source: /Users/arnon/Desktop/MITHACK/AI-­ Based Early Detection of CRAO on Retinal Images.pdf
title: AI based Detection of Central Retinal Artery Occlusion within 4.5 hours on Standard Fundus Photographs
pages: 9
---

<!-- page 1 -->

## Journal of the American Heart Association

## ORIGINAL RESEARCH

# Artificial Intelligence- Based Detection of Central Retinal Artery Occlusion Within

### 4.5 Hours on Standard Fundus Photographs

Ayse Gungor , MSc*; Ilias Sarbout , MSc*; Aubrey L. Gilbert , MD, PhD; Steffen Hamann, MD, PhD;

Pierre Lebranchu , MD, PhD; Cristina Hobeanu, MD; Philippe Gohier , MD; Catherine Vignal- Clermont, MD; Oana M. Dumitrascu , MD; Salomon- Yves Cohen , MD, PhD; Wolf A. Lagrèze , MD; Nicolas Feltgen , MD; Frank van der Heide, MD, PhD; Cédric Lamirel , MD, PhD; Jost B. Jonas , MD; Michael Obadia , MD;

Daniel Racoceanu , PhD; Dan Milea , MD, PhD

BACKGROUND: Prompt diagnosis of acute central retinal artery occlusion (CRAO) is crucial for therapeutic management and stroke prevention. However, most stroke centers lack onsite ophthalmic expertise before considering fibrinolytic treatment. This study aimed to develop, train, and test a deep learning system to detect hyperacute CRAO on retinal fundus photographs within the critical 4.5- hour treatment window and up to 24 hours after visual loss to aid in secondary stroke prevention.

METHODS: Our retrospective, cross- sectional study included 1322 color fundus photographs from 771 patients with acute visual loss due to CRAO, central retinal vein occlusion, nonarteritic anterior ischemic optic neuropathy, and healthy controls. Photographs were collected from 9 expert neuro- ophthalmology centers in 6 countries, including 3 randomized clinical trials. Training included 1039 photographs (517 patients), followed by testing on 2 data sets: (1) hyperacute CRAO (54 photographs, 54 patients) and (2) CRAO within 24 hours after visual loss (110 photographs, 109 patients).

RESULTS: The deep learning system achieved an area under the receiver operating characteristic curve of 0.96 (95% confidence interval (CI), 0.95–0.98), a sensitivity of 92.6% (95% CI, 87.0–98.0), and a specificity of 85.0% (95% CI, 81.8–92.8) for detecting CRAO at hyperacute stage, with similar results within 24 hours. The deep learning system outperformed stroke neurologists on a subset of hyperacute testing data set (120 photographs, 120 patients).

CONCLUSIONS: A deep learning system can accurately detect hyperacute CRAO on retinal photographs within a time window compatible with urgent fibrinolysis. If further validated, such systems could improve patient selection for fibrinolytic trials and optimize secondary stroke prevention.

REGISTRATION: URL: https://w ww.c linic altri als.g ov; Unique identifier: NCT06390579.

Key Words: acute stroke ■ artificial intelligence ■ central retinal artery occlusion ■ cerebrovascular stroke ■ early diagnosis ■ machine learning ■ visual loss

Correspondence to: Dan Milea, MD, PhD, Rothschild Foundation Hospital, 29 rue Manin, 75019 Paris, France. Email: visual.neurosciences@gmail.com *A. Gungor and I. Sarbout contributed equally and are co-f irst authors.

Preprint posted on MedRxiv December 23, 2024. doi: https:// doi. org/ 10. 1101/ 2024. 12. 19. 24319390.

This article was sent to Jose Rafael Romero, MD, Associate Editor, for review by expert referees, editorial decision, and final disposition. Supplemental Material is available at https:// www. ahajo urnals. org/ doi/ suppl/ 10. 1161/ JAHA. 124. 041441

For Sources of Funding and Disclosures, see page 8.

© 2025 The Author(s). Published on behalf of the American Heart Association, Inc., by Wiley. This is an open access article under the terms of the Creative Commons Attribution-NonCommercial License, which permits use, distribution and reproduction in any medium, provided the original work is properly cited and is not used for commercial purposes.

JAHA is available at: www.ahajournals.org/journal/jaha

<!-- page 2 -->

### CLINICAL PERSPECTIVE

#### What Is New?

- This study investigates the utility of deep learning applied to color fundus photographs to accurately identify acute central retinal artery occlusion.

#### What Are the Clinical Implications?

- In settings where ophthalmologic expertise is not readily available, the deep learning system can assist in early central retinal artery occlusion detection, improving patient selection for fibrinolytic trials and secondary stroke prevention.

#### Nonstandard Abbreviations and Acronyms

CRAO central retinal artery occlusion CRVO central retinal vein occlusion DLS deep learning system

NAION nonarteritic anterior ischemic optic neuropathy

entral retinal artery occlusion (CRAO) is consid- Cered an “eye stroke,”^1 causing not only sudden vi- sual loss but also an increased risk for subsequent cerebrovascular and cardiovascular events, with a peak in the first 7 days.^2–4 CRAO is a severe, blinding condition with <20% of patients experiencing meaningful visual recovery.^5,6

Currently, no randomized clinical trial (RCT) has proven an effective treatment for CRAO,^7 but early intravenous alteplase within 4.5 hours has shown recovery rates up to 50%, compared with 15.2% when administered between 4.5 and 6 hours.^8,9 Preliminary available results from a first RCT assessing intravenous fibrinolysis within 4.5 hours^10 will be soon complemented by results of 2 other ongoing trials, with the hope to provide an answer to the important question of fibrinolysis in hyperacute CRAO.^5

CRAO diagnosis requires ophthalmic expertise, which is lacking in most stroke or emergency departments, making timely diagnosis and intervention difficult.^11 Indeed, <40% of patients are initially evaluated by an ophthalmologist,^12–14 possibly explaining why treatment is often initiated late in >50% of cases,^15–17 as more than half of the patients present after the critical 4.5-h our window.^18,19 Nonophthalmic physicians often lack confidence in diagnosing CRAO,^20 which is not uncommonly associated with a normal fundus examination at the acute stage.^21–23

The advent of artificial intelligence in medical imaging offers novel opportunities to develop tools for accurate and rapid diagnosis across a variety of medical conditions. Deep learning- based artificial intelligence systems have already demonstrated excellent performance in the early recognition of stroke signs in prehospital settings,^24 and the rapid identification of ST- elevation myocardial infarction.^25 Recently, artificial intelligence- based methods applied to retinal imaging has been used as a window to identify neurological disorders such as papilledema related to raised intracranial pressure,^26,27 and dementia.^28

Our study aimed to develop, train, and test a deep learning system (DLS) for the early detection of CRAO on color fundus photographs: (1) within the critical 4.5- hour window to identify patients eligible for fibrinolysis, and (2) within the first 24 hours after visual loss, allowing improved secondary stroke prevention.

## METHODS

#### Ethics and Institutional Governance Approvals

The data that support the findings of this study are available from the corresponding author upon reasonable request. This cross- sectional study was approved by ethical committees of each contributing center and the institutional review board (IRB00012801) of the coordinating center (Rothschild Foundation Hospital, Paris, France) and is registered on Clini calTr ials.g ov (NCT06390579). It was conducted in accordance with the Declaration of Helsinki. Informed consent was waived due to the retrospective nature of the study and the use of anonymized data. This study followed the Standard Protocol Items: Recommendations for Interventional Trials–Artificial Intelligence,^29 the Consolidated Standards of Reporting Trials–Artificial Intelligence,^30 and the Strengthening the Reporting of Observational Studies in Epidemiology^31 reporting guidelines.

#### Study Design and Participants

Color fundus photographs were collected from the clinical databases of 9 expert collaborating centers worldwide, including those of patients who were prospectively enrolled in CRAO RCTs, such as the EAGLE (European Assessment Group for Lysis in the Eye),^17 THEIA (Thrombolysis in Patients With Acute Central Retinal Artery Occlusion),^32 and TenCRAOS (Tenecteplase in Central Retinal Artery Occlusion Study)^33; as well as from 2 publicly available databases.^34,35 These 11 databases included patients with diagnosis of sudden, painless visual loss (CRAO, central retinal vein occlusion [CRVO], nonarteritic anterior ischemic optic neuropathy

<!-- page 3 -->

Table 1. Data Used in the Training and Internal Validation Data Sets

|Location|Center|No. of patients|No. of photographs used by classes|Age, y, mean (range)|Sex, No. (%) Male|Sex, No. (%) Female|
|-|-|-|-|-|-|-|
|Angers, France|Angers University Hospital|157|80 normal 112 NAION|71.6 (19–95)|70 (44.6)|73 (46.5)|
|Beijing, China|Beijing Institute of Ophthalmology|6|6 normal 6 CRAO|45.5 (30–59)|4 (66.7)|2 (33.3)|
|Freiburg, Germany|Eye Center, University of Freiburg|30|50 CRAO|62.2 (24–74)|20 (66.7)|10 (33.3)|
|Nagpur, India|Suraj Eye Institute|19|19 normal 8 CRAO|54.0 (33–71)|5 (26.3)|1 (5.3)|
|Paris, France|Ophthalmic Imaging and Laser Center|68|48 CRVO 20 CRAO|76.0 (46–97)|33 (48.5)|35 (51.5)|
||Rothschild Foundation Hospital|237|32 normal 27 NAION 77 CRVO 129 CRAO|65.2 (16–93)|89 (37.5)|68 (28.7)|
|Publicly Available Data sets|Rotterdam EyePACS AIROGS|NA|305 normal|NA|NA|NA|
||Kaggle|NA|38 normal 66 CRVO 16 CRAO|NA|NA|NA|

CRAO indicates central retinal artery occlusion; CRVO, central retinal vein occlusion; NA, not available; and NAION, nonarteritic anterior ischemic optic neuropathy.

[NAION]) and healthy controls. Inclusion criteria for patients with CRAO were specifically defined. The training data set included CRAO fundus photographs that were acquired between 24 hours and 30 days after visual loss. The testing data sets included CRAO photographs that were taken within the first 24 hours after visual loss. Importantly, if CRAO photographs were taken after fibrinolysis, the patients were excluded. Healthy controls were defined as individuals with no known retinal or optic nerve pathology. For all cases, including patients with CRAO, CRVO, or NAION and healthy controls, photographs were excluded if they were taken in patients with unconfirmed diagnosis or in association with other retinal conditions or if they were of poor quality. Poor quality photographs were defined as those with artifacts, inadequate focus, poor illumination, or obscured retinal details that hindered accurate interpretation (Figure S1).

A DLS was developed, trained, and tested in a multiclass classification setting to differentiate CRAO from CRVO and NAION as well as from photographs of healthy controls. The training and internal validation data sets consisted of 1039 color fundus photographs: 614 photographs (517 patients) collected from 6 participating centers and 425 photographs (16 CRAO, 66 CRVO, and 343 normal) from 2 publicly available databases. The participating centers contributed by providing 213 CRAO (164 patients), 125 CRVO (125 patients), 139 NAION (124 patients), and 137 normal (104 patients) photographs (Table 1). We tested our DLS on CRAO images at 2 distinct timelines: within 4.5 hours after visual loss and within 24 hours after visual loss. The

first testing data set included 54 CRAO photographs (54 patients) taken within 4.5 hours after visual loss, 63 photographs (63 patients) with CRVO, 50 photographs (41 patients) with NAION, and 60 photographs (41 patients) of healthy controls. The second testing data set included a total of 110 CRAO photographs (109 patients whose photographs were captured within 24 hours after visual loss, comprising 54 photographs from the first data set and an additional 56 photographs from 55 patients photographed between 4.5 and 24 hours), 63 CRVO photographs (63 patients), 50 NAION photographs (41 patients), along with 60 photographs (41 patients) of healthy controls (Table 2). All photographs in the testing data sets were independent of those used in the training and internal validation data sets.

#### Development of the DLS

The DLS employed a convolutional neural network, optimized through a grid search on an internal validation set to determine the most effective combination of hyperparameters of the model, including batch size, learning rate, network size, cross- entropy weights, number of epochs, and a set of data augmentation techniques. The architecture, detailed in Figure S2, included strided and classic convolutional layers, rectified linear unit activation functions,^36 fully connected layers, and a SoftMax layer, which outputs a score for each of the 4 predicted classes.^37 Dropout was used to prevent overfitting. To visualize the model’s decisionmaking process, the gradient- based approach gradient- weighted class activation map^38 was applied

<!-- page 4 -->

Table 2. Data Used in the Testing Data Sets

|Location|Center|No. of patients|No. of photographs used by classes|Age, y, mean (range)|Sex, No. (%) Male|Sex, No. (%) Female|
|-|-|-|-|-|-|-|
|Angers, France|Angers University Hospital|52|37 normal 43 NAION|71.8 (48–93)|24 (46.2)|28 (53.8)|
|Copenhagen, Denmark*|University of Copenhagen|7|7 CRAO <4.5h 7 CRAO <24h|67.2 (51–79)|4 (57.1)|3 (42.9)|
|Freiburg, Germany|Eye Center, University of Freiburg|25|11 CRAO <4.5h 25 CRAO <24h|61.5 (24–74)|19 (76.0)|6 (24.0)|
|Nantes, France*|Nantes University Hospital|20|4 CRAO <4.5h 20 CRAO <24h|72.0 (54–87)|12 (60.0)|8 (40.0)|
|Paris, France|Ophthalmic Imaging and Laser Center|28|26 CRVO 2 CRAO <24h|77.1 (53–100)|16 (57.1)|12 (42.9)|
||Rothschild Foundation Hospital|58|3 normal 7 NAION 33 CRVO 3 CRAO <4.5h 15 CRAO <24h|65.0 (16–87)|16 (27.6)|8 (13.8)|
|Vallejo, California, US*|Kaiser Permanente Northern California|64|20 normal 4 CRVO 29 CRAO <4.5h 41 CRAO <24h|64.8 (32–93)|37 (57.8)|27 (42.2)|

CRAO indicates central retinal artery occlusion; CRVO, central retinal vein occlusion; NA, not available; and NAION, nonarteritic anterior ischemic optic neuropathy.

*External centers which have contributed exclusively to the testing data sets.

to all individual displays within each class, and the resulting heatmaps were averaged to generate diseasespecific class- activation maps. These maps highlighted the areas with the highest pixel activation, helping to identify key image features that influenced the model’s decisions. This visual representation allowed us to align these regions with pathological cues typically assessed by experts. The performance of the DLS was calculated via the area under the receiver operating characteristic curve, sensitivity, specificity, accuracy, and F- 1 score. To estimate the 95% confidence interval (CI) of the performance metrics, bootstrapping (2000 iterations) with the eye as the sampling unit was employed. The performance of the DLS was tested at 2 levels: (1) on data collected from centers that have been involved in both training and testing data sets (but no overlap between photographs used in training and testing); and (2) on a data set from centers that have contributed exclusively with photographs for testing.

#### Preprocessing for Enhancing the DLS’s Robustness

Color fundus photographs are often captured under variable lighting conditions, resulting in uneven illumination caused by shadows, reflections, etc. affecting the quality of feature extraction. Such variations in colorimetric properties and contrast may also occur due to different camera models (Table S1). To address these challenges and enhance the robustness of our DLS, several preprocessing steps were implemented.

First, contrast- limited adaptive histogram equalization,^39 a gold- standard preprocessing technique for fundus photographs, was applied to the luminance channel in the LAB color space to enhance local contrast. This method helped prevent overamplification of noise in low- contrast areas by adaptively adjusting the contrast. Next, a novel approach for background removal was introduced, leveraging recent advancements in DL methodologies,^40 to improve the generalizability of the DLS by addressing variability in colorimetric properties across different cameras and retinal pigmentation. This helped eliminate irrelevant background information, such as uneven illumination or artifacts, while preserving the essential retinal structures required for accurate classification. To achieve this, image dilation was applied, followed by median blurring to estimate the background, which was subsequently subtracted from the original image (Figure 1). To further enhance the robustness of the DLS, various data augmentation techniques were randomly applied during the training, including random cropping, homographies, and adjustments to contrast and color.

#### Evaluation by Stroke Neurologists for Comparative Analysis

We compared the performance of the DLS at 4.5 hours with that of 3 expert stroke neurologists (G.A., C.S., and C.H.) who were chosen because of their everyday role in managing CRAO cases. Following a brief training session, each evaluating stroke neurologist independently

<!-- page 5 -->

![Figure 1. Preprocessing of the color fundus photographs. Original fundus photographs, taken with 2 different cameras in 2 patients with central retinal artery occlusion (top row). The bottom row repre…](/Users/arnon/Library/Caches/anymd/images/6306cd59426547a5.jpg)
<!-- image: 1890x1768, page 5 -->

Figure 1. Preprocessing of the color fundus photographs.

Original fundus photographs, taken with 2 different cameras in 2 patients with central retinal artery occlusion (top row). The bottom row represents the corresponding preprocessed images, after the custom background removal.

classified a subset of 120 color fundus photographs (120 patients) from the first testing data set. This subset included 30 hyperacute CRAO photographs (30 patients) taken within 4.5 hours after visual loss, 30 CRVO photographs (30 patients), 30 NAION photographs (30 patients), and 30 normal photographs (30 patients). The classifications were performed into 4 classes using the semiautomated image annotation application, Classif- Eye.^41 The stroke neurologists were masked to the patients’ clinical information and unaware of the classifications made by the DLS or the other stroke neurologists. The overall agreement among the 3 stroke neurologists was assessed using the Fleiss kappa score.^42 The kappa

agreement score was interpreted based on a previously published scale: 0 to 0.20 indicating no agreement, 0.21 to 0.39 minimal agreement, 0.40 to 0.59 weak agreement, 0.60 to 0.79 moderate agreement, 0.80 to 0.90 strong agreement, and scores exceeding 0.90 indicating almost perfect agreement.^43 Additionally, a Z- test was performed to compare the performance of the DLS and the stroke neurologists, evaluating the null hypothesis that the DLS performs worse than the stroke neurologists. To account for multiple comparisons, Fisher’s method was applied to combine the P values obtained from the Z- tests, ensuring a robust statistical evaluation of the DLS’s performance.

<!-- page 6 -->

![Figure 2. Superimposed and averaged disease- specific class- activation maps. Superimposed and averaged class- activation maps, revealing areas of interest with highest pixel activation to differentia…](/Users/arnon/Library/Caches/anymd/images/c57218dd3ef7c06b.jpg)
<!-- image: 1902x500, page 6 -->

Figure 2. Superimposed and averaged disease- specific class- activation maps.

Superimposed and averaged class- activation maps, revealing areas of interest with highest pixel activation to differentiate between (A) normal, (B) central retinal artery occlusion, (C) central retinal vein occlusion, and (D) nonarteritic anterior ischemic optic neuropathy.

## RESULTS

#### Patient Characteristics

From the initially available 2861 CRAO photographs and 827 non CRAO photographs collected from the participating neuro- ophthalmology centers (excluding public data sets), 2538 CRAO photographs (88.7%) and 253 non CRAO photographs (30.6%) were removed based on exclusion criteria (Figure S1).

Demographic details were available for 630 of 771 included patients. The training and internal validation data sets consisted of 221 (42.7%) male individuals, 189 (36.6%) female individuals, with a mean (range) age of 68.1 (16–97) years (Table 1). The testing data sets included 128 (50.4%) male individuals and 92 (36.2%) female individuals, with a mean (range) age of 68.5 (16–

100) years (Table 2). Demographic details by condition in the training and testing data sets can be found in Table S2.

#### Classification Performance and Statistical Analysis

In a one- versus- rest model, the DLS distinguished CRAO cases from non CRAO cases (including CRVO, NAION, and healthy controls) with an accuracy of 86.8% (95% CI, 77.4–92.6), misclassifying only 4 out of 54 CRAO photographs taken within 4.5 hours visual loss (Figure S3). The area under the receiver operating characteristic curve for this task was 0.96 (95% CI, 0.95–0.98), with a sensitivity of 92.6% (95% CI, 87.0– 98.0), a specificity of 85.0% (95% CI, 81.8–92.8), and a binary F- 1 score of 76.9% (95% CI, 70.3–85.8). The performance at 24 hours after visual loss showed that the DLS achieved an area under the receiver operating characteristic curve of 0.97 (95% CI, 0.96–0.99), a sensitivity of 94.5% (95% CI, 88.3–99.0), a specificity of 85.0% (95% CI, 81.8–92.8), an accuracy of 88.7% (95% CI, 78.5–95.9), and a binary F- 1 score of 86.7%

(95% CI, 83.4–93.7) (Figure S4). The results for the DLS’s performance in detecting other classes, including CRVO, NAION, and healthy controls, can be found in Figure S5. To further evaluate the generalizability of the DLS and minimize the risk of overfitting, an additional external testing was conducted by removing all internal testing images from centers that also contributed to the training data set. On this fully independent external data set, the DLS achieved an accuracy of 92.6% (95% CI, 81.4–99.6) in detecting CRAO cases, reinforcing its robustness and ability to generalize beyond the training data (Table S3). Notably, 2 out of 3 centers included in this external data set participated in RCTs,^32,33 further strengthening the reliability of the data set and the DLS’s performance. The averaged disease- specific classactivation maps highlighted the regions of interest with the highest pixel activation for each condition. In healthy controls, the entire retina showed diffuse pixel activation (Figure 2A). In CRAO cases, the highest pixel activation was in the macular region (Figure 2B). In CRVO cases, pixel activation was broadly distributed in the circumferential peripheral part of the macular region (Figure 2C), whereas in NAION cases, pixel activation was concentrated in the optic disc zone (Figure 2D).

Among the 199 patients included at <4.5 hours after visual loss, a subset of 120 patients (30 with CRAO, 30 with CRVO, 30 with NAION and 30 healthy controls) were evaluated by both the DLS and the stroke neurologists. The DLS detected all 30 CRAO cases, achieving an accuracy of 85% (95% CI, 71.3–90.8), sensitivity of 100% (95% CI, 88.4–100.0), and specificity of 80% (95% CI, 70.1–85.3). In comparison, the stroke neurologists’ performance on the same task showed accuracy ranging from 66.7% to 79.2%, sensitivity from 50% to 63.3%, and specificity from 72.2% to 84.4% (Figure 3). The classifications made by both the DLS and the stroke neurologists, including accurate classifications and misclassifications for cases with and without CRAO, are provided in Figure S6. The intergrader

<!-- page 7 -->

![Figure 3. Performance (accuracy, sensitivity, specificity) of the deep learning system and the 3 stroke neurologists in detecting hyperacute central retinal artery occlusion. Comparison of the perform…](/Users/arnon/Library/Caches/anymd/images/b99be074a84b6fbe.png)
<!-- image: 1949x755, page 7 -->

Figure 3. Performance (accuracy, sensitivity, specificity) of the deep learning system and the 3 stroke neurologists in detecting hyperacute central retinal artery occlusion.

Comparison of the performance (accuracy, sensitivity, specificity) of the deep learning system to the performance of each stroke neurologist in detecting hyperacute CRAO from other differential diagnosis of sudden, painless visual loss (central retinal vein occlusion and nonarteritic anterior ischemic optic neuropathy) and from healthy controls on 120 color fundus photographs (30 cases with hyperacute CRAO and 90 cases without CRAO). CRAO indicates central retinal artery occlusion; DLS, deep learning system; and SN, stroke neurologist.

agreement was moderate, with a kappa score of 0.73. Disagreement among stroke neurologists was noted in 18 photographs, including 5 (27.7%) photographs of hyperacute CRAO. Statistical analysis resulted in a P value of 0.0002, leading to the rejection of the null hypothesis, suggesting that the DLS performs at least as well as, if not better than, the stroke neurologists at detecting CRAO at the hyperacute stage.

## DISCUSSION

The main finding of our study is that a DLS can effectively identify CRAO at both hyperacute (4.5 hours) and delayed (24 hours) stages, distinguishing it from photographs of healthy controls and from other differential diagnosis of sudden, painless visual loss such as CRVO and NAION. The DLS accurately identified CRAO cases, missing only 4 out of 54 CRAO photographs (7.4%) taken within 4.5 hours and 6 out of 110 photographs (5.4%) taken within 24 hours after visual loss. The performance of the DLS was at least as well as if not better than the stroke neurologists, suggesting that such a system could potentially serve an assistive aid in an emergency setting.

Superimposed and averaged disease- specific class- activation maps highlighted the regions of interest with the highest pixel activations, indicating the areas of the images most critical for the DLS’s predictions. This method has already been used as an innovative way to determine areas of interest in similar diagnostic

applications.^44 In healthy controls, the DLS established the diagnosis using averaged class- activation maps that were distributed over the whole retina (Figure 2A). Conversely, in CRAO cases the highest area of interest was limited to the macular region (Figure 2B), which is indeed preferentially affected in CRAO. In CRVO cases, pixel activation was broadly distributed in the circumferential peripheral part of the macular region, reflecting the widespread retinal hemorrhages (Figure 2C). Lastly, in NAION, the region of interest was unsurprisingly concentrated in the region of the optic nerve head, where hemorrhages and edema are clinically seen (Figure 2D). Thus, the areas highlighted by the DLS’s superimposed and averaged class- activation maps align with the primary anatomical sites affected by each specific condition.

The overall accuracy of the DLS was 87% in detecting CRAO at the hyperacute stage. Importantly, many of the CRAO photographs in this testing data set were collected prospectively in validated prospective RCTs, evaluating fibrinolytic treatments in this condition.^17,32,33 Identification of patients at the hyperacute stage remains challenging, primarily due to delayed presentation or CRAO diagnosis, which is one of the reasons for delayed inclusions. Indeed, in the EAGLE trial, the mean time from symptom onset to presentation was 9.5 hours, with a mean of 11 hours to treatment.^17 Our study, which represents one of the largest CRAO studies to day, suggests that such an automated assistive system may improve early identification of CRAO in the future, with therapeutic implications.

<!-- page 8 -->

#### Limitations

Our study has inherent limitations. The training was performed on a retrospectively collected data set study, excluding those with multiple ophthalmic pathologies, limiting the study’s ability to generalize its findings to real life situations. We used standard fundus photography as a method to identify CRAO. Although optical coherence tomography is a more sensitive modality for detecting acute CRAO, capable of identifying subtle retinal changes not visible on fundus photographs,^21 it was not included in this study due to its high cost and the expertise required for image acquisition and interpretation, which limit its availability in many emergency settings. Additionally, we used only photographs taken with traditional cameras, which means that data acquired with wide- angle and handheld cameras will need further investigation. All the patients included in the testing data set had abnormal ophthalmoscopic findings at the hyperacute stage, consistent with inclusion criteria in previously published studies. The DLS was able to 17,32,33

accurately exclude other causes of acute visual loss (ie, NAION, CRVO), aiming to further support a presumptive diagnosis of CRAO in the setting of a compelling clinical

Scottsdale, Arizona (O.M.D.); Ophthalmic Imaging and Laser Center (CIL), Paris, France (S-Y.C.); Eye Center, Medical Center, Medical Faculty, University of Freiburg, Freiburg, Germany (W.A.L.); Eye Clinic, Medical Center, University of Gottingen, Gottingen, Germany (N.F.); Eye Clinic, Basel University Hospital, Basel, Switzerland (N.F.); Epidemiology of Ageing and Neurodegenerative Diseases, Université Paris Cité, Inserm U1153, Paris, France (F.v.d.H.); Institut Français de Myopie, Rothschild Foundation Hospital, Paris, France (J.B.J.); andSingapore Eye Research Institute, Singapore National Eye Center, Singapore (J.B.J.).

## Acknowledgments

We thank VISIO Foundation, France for supporting this study; as well as Bouchra Touzani, MSc and Emmanuel Blondel, MSc at the Rothschild Foundation Hospital for their valuable assistance during this study.

Sources of Funding

This study was supported by a research grant from VISIO Foundation (Fondation VISIO pour l’aide aux enfants et aux adultes déficients visuels), France.

Disclosures

Dan Milea is an advisory board member of Optomed, Finland.

Supplemental Material

Tables S1–S3

Figures S1–S6

## REFERENCES

history and presence of relative afferent pupillary defect. 1. Mac Grory B, Schrag M, Biousse V, Furie KL, Gerhard- Herman M,

However, we recognize that our DLS may have failed to detect those patients with CRAO who presented normal fundi and who might be the most suitable for fibrinolysis

Lavin PJ, Sobrin L, Tjoumakaris SI, Weyand CM, Yaghi S. Management of central retinal artery occlusion: a scientific statement from the American Heart Association. Stroke. 2021;52:e282–e294. doi: 10.1161/ STR.0000000000000366

due to their viable retina. 2. Fallico M, Lotery AJ, Longo A, Avitabile T, Bonfiglio V, Russo A, Murabito

## CONCLUSIONS

P, Palmucci S, Pulvirenti A, Reibaldi M. Risk of acute stroke in patients with retinal artery occlusion: a systematic review and meta- analysis. Eye. 2019;34:683–689. doi: 10.1038/s41433- 019- 0576- y

3. Lavin P, Patrylo M, Hollar M, Espaillat K, Kirshner H, Schrag M. Stroke risk and risk factors in patients with central retinal artery occlusion. Am J Ophthalmol. 2019;200:271–272. doi: 10.1016/j.ajo.2019.01.021

A DLS can detect CRAO at both the hyperacute (within 4. Park SJ, Choi N- K, Yang BR, Park KH, Lee J, Jung S- Y, Woo SJ. Risk

4.5 hours after visual loss) and the delayed stage (within 24 hours) using color fundus photographs. Beyond aid-

and risk periods for stroke and acute myocardial infarction in patients with central retinal artery occlusion. Ophthalmology. 2015;122:2336– 2343.e2. doi: 10.1016/j.ophtha.2015.07.018

ing in CRAO diagnosis, the DLS can also improve pa- 5. Schrag M, Youn T, Schindler J, Kirshner H, Greer D. Intravenous fi-

tient selection for fibrinolytic trials and secondary stroke prevention. Future prospective studies are necessary to validate the performance of the DLS, at best in real- life conditions.

ARTICLE INFORMATION

Received February 7, 2025; accepted April 25, 2025.

brinolytic therapy in central retinal artery occlusion. JAMA Neurol. 2015;72:1148. doi: 10.1001/jamaneurol.2015.1578

6. Hayreh SS, Zimmerman MB. Central retinal artery occlusion: visual outcome. Am J Ophthalmol. 2005;140:376.e1. doi: 10.1016/j.ajo. 2005. 03.038

7. Hayreh SS, Zimmerman MB, Kimura A, Sanon A. Central retinal artery occlusion. Exp Eye Res. 2004;78:723–736. doi: 10.1016/ S0014- 4835(03)00214- 8

8. Shahjouei S, Bavarsad Shahripour R, Dumitrascu OM. Thrombolysis for central retinal artery occlusion: an individual participant- level metaanalysis. Int J Stroke. 2024;19:29–39. doi: 10.1177/17474930231189352

Affiliations 9. Mac Grory B, Nackenoff A, Poli S, Spitzer MS, Nedelmann M, Guillon B,

Department of Neuro- Ophthalmology (A.G., I.S., C.V., F.v.d.H., C.L., D.M.), and Rothschild Computational and Visual Neurosciences Laboratory, Rothschild Foundation Hospital, Paris, France (A.G., I.S., F.v.d.H., D.M.); Sorbonne

Preterre C, Chen CS, Lee AW, Yaghi S, et al. Intravenous fibrinolysis for central retinal artery occlusion. Stroke. 2020;51:2018–2025. doi: 10.1161/ STROKEAHA.119.028743

Université, Institut du Cerveau—Paris Brain Institute—ICM, Inria, Inserm, 10. Guillon B, Preterre C, Obadia M, Mourand I, Gaudron M, Sablot D,

CNRS, APHP, Hôpital de la Pitié Salpêtrière, Paris, France (A.G., I.S., D.R.); Kaiser Permanente Northern California, Vallejo, California (A.L.G.); Department of Ophthalmology, Copenhagen University Hospital—Rigshospitalet, Glostrup, Denmark (S.H.); Department of Clinical Medicine, University of

Godeneche G, Marc G, Rodier G, Urbanczyk C, et al. Oral communication at the 16th World Stroke Congress. A randomized controlled trial of alteplase initiated within 4.5 hours of central retinal artery occlusion. THEIA Study. 2024.

Copenhagen, Copenhagen, Denmark (S.H.); Nantes Université, Service 11. Youn TS, Lavin P, Patrylo M, Schindler J, Kirshner H, Greer DM, Schrag

d’Ophtalmologie CHU Nantes, École Centrale Nantes, LS2N, UMR6004, Nantes, France (P.L.); Department of Neurology, Rothschild Foundation

M. Current treatment of central retinal artery occlusion: a national survey. J Neurol. 2017;265:330–335. doi: 10.1007/s00415- 017- 8702- x

Hospital, Paris, France (C.H., M.O.); Department of Ophthalmology, University 12. Flowers AM, Chan W, Meyer BI, Bruce BB, Newman NJ, Biousse V.

Hospital, Angers, France (P.G.); Department of Neurology, Mayo Clinic,

Referral patterns of central retinal artery occlusion to an academic center

<!-- page 9 -->

||affiliated with a stroke center. J Neuroophthalmol. 2021;41:480–487. doi:|deep learning model for detection of Alzheimer’s disease based on reti-|
|-|-|-|
||10.1097/WNO.0000000000001409|nal photographs: a retrospective, multicentre case- control study. Lancet|
|13.|Shah R, Gilbert A, Melles R, Patel A, Do T, Wolek M, Vora RA. Central ret-|Digital Health. 2022;4:e806–e815. doi: 10.1016/S2589-7 500(22)00169-8|

inal artery occlusion. Ophthalmol Retina. 2023;7:527–531. doi: 10.1016/j. 29. Cruz Rivera S, Liu X, Chan A- W, Denniston AK, Calvert MJ, Darzi A,

oret.2023.01.005 14. PC, Frohman LP. ophthalmic care. J

DeBusk A, Subramanian PS, Scannell Bryan M, Moster ML, Calvert Mismatch in supply and demand for neuro- Neuroophthalmol. 2021;42:62–67. doi: 10.1097/

Holmes C, Yau C, Moher D, Ashrafian H, et al. Guidelines for clinical trial protocols for interventions involving artificial intelligence: the SPIRIT-A I extension. Nat Med. 2020;26:1351–1363. doi: 10.1038/ s41591-0 20-1 037-7

WNO.0000000000001214 30. Liu X, Cruz Rivera S, Moher D, Calvert MJ, Denniston AK, Chan A- W,

15. Hoyer C, Kahlert C, Güney R, Schlichtenbrede F, Platten M, Szabo K. Central retinal artery occlusion as a neuro- ophthalmological emergency: the need to raise public awareness. Eur J Neurol. 2021;28:2111–2114. doi: 10.1111/ene.14735

Darzi A, Holmes C, Yau C, Ashrafian H, et al. Reporting guidelines for clinical trial reports for interventions involving artificial intelligence: the CONSORT- AI extension. Nat Med. 2020;26:1364–1374. doi: 10.1038/ s41591-0 20-1 034-x

16. Lee KE, Tschoe C, Coffman SA, Kittel C, Brown PA, Vu Q, Fargen 31. von Elm E, Altman DG, Egger M, Pocock SJ, Gøtzsche PC,

KM, Hayes BH, Wolfe SQ. Management of acute central retinal artery occlusion, a “retinal stroke”: an institutional series and literature review. J Stroke Cerebrovasc Dis. 2021;30:105531. doi: 10.1016/j. jstrokecerebrovasdis.2020.105531

Vandenbroucke JP. Strengthening the reporting of observational studies in epidemiology (STROBE) statement: guidelines for reporting observational studies. BMJ (Clinical Research Ed). 2007;335:806–808. doi: 10.1136/bmj.39335.541782.AD

17. Mueller AJ. Evaluation of minimally invasive therapies and rationale for 32. A Phase III Randomized, Blind, Double Dummy, Multicenter Study

a prospective randomized trial to evaluate selective intra- arterial lysis for clinically complete central retinal artery occlusion. Arch Ophthalmol. 2003;121:1377. doi: 10.1001/archopht.121.10.1377

Assessing the Efficacy and Safety of IV THrombolysis in Patients With acutE Central retInal Artery Occlusion ClinicalTrials.gov Identifier: NCT03197194.

(Alteplase) (THEIA) -

18. Schumacher M, Schmidt D, Jurklies B, Gall C, Wanke I, Schmoor C, 33. TENecteplase in Central Retinal Artery Occlusion Stuy (TenCRAOS) - Maier- Lenz H, Solymosi L, Brueckmann H, Neubauer AS, et al. Central ClinicalTrials.gov Identifier: NCT04526951.

retinal artery occlusion: local intra- arterial fibrinolysis versus con- 34. de Vente C, Vermeer KA, Jaccard N, Wang H, Sun H, Khader F, Truhn D,

||servative treatment, a multicenter randomized trial. Ophthalmology.|Aimyshev T, Zhanibekuly Y, Le T- D, et al. AIROGS: Artificial Intelligence|
|-|-|-|
||2010;117:1367–1375.e1. doi: 10.1016/j.ophtha.2010.03.061|for RObust Glaucoma Screening Challenge. IEEE Trans Med Imaging.|
|19.|Chan W, Flowers AM, Meyer BI, Bruce BB, Newman NJ, Biousse V.|2024;43:542–557. doi: 10.1109/TMI.2023.3313786|

Acute central retinal artery occlusion seen within 24 hours at a tertiary 35. Cen L- P, Ji J, Lin J- W, Ju S- T, Lin H- J, Li T- P, Wang Y, Yang J- F, Liu

||institution. J Stroke Cerebrovasc Dis. 2021;30:105988. doi: 10.1016/j.|Y- F, Tan S, et al. Automatic detection of 39 fundus diseases and condi-|
|-|-|-|
||jstrokecerebrovasdis.2021.105988|tions in retinal photographs using deep neural networks. Nat Commun.|
|20.|Uhr JH, Governatori NJ, Zhang Q; Ed, Hamershock R, Radell JE, Lee|2021;12:4828.|

JY, Tatum J, Wu AY. Training in and comfort with diagnosis and man- 36. Mesran M, Yahya SR, Nugroho F, Windarto AP. Investigating the impact

agement of ophthalmic emergencies among emergency medicine physicians in the United States. Eye. 2020;34:1504–1511. doi: 10.1038/ s41433- 020- 0889- x

of ReLU and sigmoid activation functions on animal classification using CNN models. Jurnal RESTI (Rekayasa Sistem Dan Teknologi Informasi). 2024;8:111–118. doi: 10.29207/resti.v8i1.5367

21. Fan W, Huang Y, Zhao Y, Yuan R. Central retinal artery occlusion with- 37. Li P, Jing R, Shi X. Apple disease recognition based on convolutional

|out cherry- red spots. BMC Ophthalmol. 2023;23:434. doi: 10.1186/|neural networks with modified Softmax. Front Plant Sci. 2022;13:820146.|
|-|-|
|s12886-0 23-0 3176-w|doi: 10.3389/fpls.2022.820146|

22. Hayreh SS, Zimmerman MB. Fundus changes in central retinal artery 38. Selvaraju RR, Cogswell M, Das A, Vedantam R, Parikh D, Batra D. Grad-

||occlusion. Retina. 2007;27:276–289. doi: 10.1097/01.iae.0 0002 380 95.|CAM: Visual Explanations from Deep Networks via Gradient- Based|
|-|-|-|
||97104.9b|Localization. 2017 IEEE International Conference on Computer Vision|
|23.|Abdellah MM. Multimodal imaging of acute central retinal artery occlu-|(ICCV). 2017:618–626. doi: 10.1109/ICCV.2017.74|

sion. Med Hypothesis Discov Innov Ophthalmol. 2019;8:283–290. 39. Hayati M, Muchtar K, Roslidar, Maulina N, Syamsuddin I, Elwirehardja

|24.|Wenstrup J, Havtorn JD, Borgholt L, Blomberg SN, Maaloe L, Sayre MR,|GN, Pardamean B. Impact of CLAHE- based image enhancement for di-|
|-|-|-|
||Christensen H, Kruuse C, Christensen HC. A retrospective study on ma-|abetic retinopathy classification through deep learning. Proc Comp Sci.|
||chine learning- assisted stroke recognition for medical helpline calls. NPJ|2023;216:57–66. doi: 10.1016/j.procs.2022.12.111|

Digital Med. 2023;6:235. doi: 10.1038/s41746- 023- 00980- y 40. Hemelings R, Wong DWK, Eijgen JV, Chua J, Breda JB, Stalmans I,

25. Lin C, Liu W- T, Chang C- H, Lee C- C, Hsing S- C, Fang W- H, Tsai D- J, Chen K- C, Lee C- H, Cheng C- C, et al. Artificial intelligence–powered rapid identification of ST- elevation myocardial infarction via electrocardiogram (ARISE)—a pragmatic randomized controlled trial. NEJM Ai.

Schmetterer L. Predicting glaucomatous visual field progression from baseline fundus photos using deep learning. ARVO Annual Meeting Abstract, June 2023. Investigative Ophthalmology & Visual Science. 2023 380. https://i ovs.a rvojo urnal s.o rg/a rticl e.a spx?a rticl eid=2 790046.

2024;1:AIoa2400190. doi: 10.1056/AIoa2400190 41. Milea L, Najjar RP. Classif- Eye. GitHub. 2020 https://g ithub.c om/m ilea

26. Milea D, Najjar RP, Jiang Z, Ting D, Vasseneix C, Xu X, Aghsaei Fard leona rd/ Class if- Eye.

M, Fonseca P, Vanikieti K, Lagrèze WA, et al. Artificial intelligence to 42. Vanbelle S. Asymptotic variability of (multilevel) multirater kappa coeffidetect papilledema from ocular fundus photographs. N Engl J Med. cients. Stat Methods Med Res. 2018;28:3012–3026.

2020;382:1687–1695. doi: 10.1056/NEJMoa1917130 43. McHugh ML. Interrater reliability: the kappa statistic. Biochem Med.

27. Vasseneix C, Nusinovici S, Xu X, Hwang J- M, Hamann S, Chen JJ, Loo 2012;22:276–282. doi: 10.1016/j.jocd.2012.03.005

JL, Milea L, Tan KBK, Ting DSW, et al. Deep learning system outperforms 44. Gungor A, Najjar RP, Hamann S, Tang Z, Lagrèze WA, Sadun R,

clinicians in identifying optic disc abnormalities. J Neuroophthalmol. 2023;43:159–167. doi: 10.1097/WNO.0000000000001800 28. Cheung CY, Ran AR, Wang S, Chan VTT, Sham K, Hilal S, Venketasubramanian N, Cheng C- Y, Sabanayagam C, Tham YC, et al. A

Sathianvichitr K, Dinkin MJ, Oliveira C, Li A, et al. Deep learning to discriminate arteritic from nonarteritic ischemic optic neuropathy on color images. JAMA Ophthalmol. 2024;142:1073–1079. doi: 10.1001/ jamaophthalmol.2024.4269

