# Verification: `crao-ai-detection-prototype-cited.md`

Scope: claim-by-claim check of the cited brief against the four research notes (`research-{literature,clinical,data,build}.md`) and the base paper (`CRAO-AI-detection.md`). URLs were not re-fetched. The prototype self-checks were re-run locally (see the end). Verifier date: 2026-10-17.

**Bottom line:** no FATAL issues. Almost every number in the brief traces to a note or to the base paper. The main problems are:
- one misleading comparison in the executive summary;
- two places where the brief says the code does something it does not;
- one licensing claim that drops a caveat from the data note;
- a few ranges and "none exists" statements that go further than the notes.

---

## Part 1: Structured review

### Summary
The brief argues that the base JAHA 2025 CRAO model fixes the "reading" problem but not the care pathway. It reframes the value of fast detection: since THEIA and TenCRAOS were null, the payoff is a same-day stroke work-up rather than thrombolysis. It proposes a rule-based "Eye-Stroke Navigator" wrapper and documents a small Gradio prototype. Its evidence comes from four research notes, and the checked numbers match them closely.

### Strengths
- [S1] **The trial numbers are faithful to the clinical note.** THEIA 66% vs 48%, p=0.95, n=70, "likely underpowered". TenCRAOS 20% vs 24%, p=0.69, one fatal ICH. REVISION ≤12 h, n=127, terminated for futility. All match `research-clinical.md` lines 85–87.
- [S2] **The base-paper facts match the full text.** 1,039 training photos (614 from 517 patients at 6 centres, plus 425 public). Training CRAO photos taken 24 h–30 d after onset. AUC 0.96, sensitivity 92.6%, specificity 85.0%. Poor-quality and multi-pathology images excluded, standard cameras only, and every test CRAO had an abnormal fundus. Data "upon reasonable request". Sources: `CRAO-AI-detection.md` lines 25–29, 79, 102–106 and 207.
- [S3] **The caveats are carried through honestly.** The AHA 2b wording is flagged as secondary, ESO's "recommend" vs "suggest" conflict is noted, the absolute stroke risk (2.2%) is set against IRR 44.5, the agent papers are flagged as preprints, and the brief says "no accuracy measured".
- [S4] **The dataset counts trace to local counts in `research-data.md`.** RFMiD 1.0: CRVO 45, BRVO 119, ODE 96, AION 26, normal 669. Mendeley RAO set: 127 + 16 + 8 = 151. EyeQ: 28,792.
- [S5] **The prototype claims reproduced.** `triage.py` printed "triage self-check OK" (10 asserts). `vision.py` printed good=0.91, blurry=0.03, dark=0.00. The library versions are torch 2.14.1, timm 1.0.30, gradio 6.30.0 and opencv 5.0.0, as stated.

### Weaknesses

- [W1] **MAJOR: the AI vs neurologist comparison mixes two test sets.** The executive summary says the model reached "sensitivity 92.6% (50 of 54) where three stroke neurologists reached 50–63.3%".
  - The neurologists were tested on a different subset: 120 photos containing 30 CRAO. On that subset the model scored 100% sensitivity, 80% specificity and 85% accuracy (`CRAO-AI-detection.md` lines 151 and 180).
  - The 92.6% figure comes from the full 54-CRAO set, which the neurologists never read.
  - Putting the two side by side implies a same-set comparison that did not happen.

- [W2] **MAJOR: the brief says the code never lets a normal photo reassure, but it can.** The executive summary says "a normal-looking photo never reassures a patient with sudden one-eye vision loss". In `triage.py:73`, the escalation only fires when `onset is not None and onset <= 24`. I checked this directly:
  - A low P(CRAO) with sudden loss and **unknown onset** returns **ROUTINE**.
  - The same case at 30 h also returns ROUTINE.

  Unknown onset is common in CRAO (people wake up with it, or present late). This is a safety gap between the claim and the code. The §3 table's narrower wording ("<24 h escalates") matches the code. The executive summary and the flowchart branch ("low + fitting story → ESCALATE") do not.

- [W3] **MAJOR: the GCA "branch" does not override the stroke pathway, so the card contradicts itself.** The brief describes "GCA red-flag branch → … not a lysis candidate", lists it as "built", and uses "GCA ticked → steroid branch" in the demo script. In the code, a GCA flag only appends an action (`triage.py:39–41`). It does not change the triage level. I checked `Case(0.9, 0.9, 2.0, gca_symptoms=True)`:
  - It returns level **STROKE_PATHWAY**.
  - The first action is "Activate stroke team now … thrombolysis … decide per local protocol".
  - The second action is "NOT a thrombolysis candidate".

  A judge ticking GCA during the demo will see contradictory instructions on the same card.

- [W4] **MAJOR: the "commercially safer stack" claim drops the data note's rights caveat.** §5 says "FLAIR (Apache-2.0) plus CC BY datasets is the commercially safer stack". `research-data.md:134` adds: "Even so, the Mendeley set's web-crawled and JSIEC content may carry third-party rights". `research-data.md:54/138` adds that the JSIEC licence conflicts (Kaggle tags it ODbL, but the description says "copyright … belongs to JSIEC"). The Mendeley set is the brief's **only** RAO source (§4 data recipe), and 127 of its 151 images are web-crawled. So the CC BY 4.0 label on that row overstates how clean the licensing is.

- [W5] **MAJOR: the brain-infarct range is selectively narrowed.** The executive summary says "15–32% have acute or silent brain infarcts on MRI [7][8][9]". The clinical note (lines 108–110) gives a wider picture:
  - Its own summary range is "roughly 7–32%, depending on setting and selection".
  - The population-based Olmsted cohort found 6.7%, and the Emory cohort found 18%.
  - The three studies cited mix different groups: RAO, all "retinal ischemia", and CRAO patients who had MRI.

  In a pitch slide, the narrowed range overstates the yield.

- [W6] **MAJOR: a key rule rests on one small study.** The "Normal photo ≠ safe" rule (§3 #2: "Photos missed ~31% of early ischaemia vs OCT") and the §1 gap paragraph both rest on one Emory protocol paper [16], where the <4.5 h group was **n=16** (11/16). The brief gives "11/16" in §1 but drops the n in the §3 table. The rule itself is also supported by Hayreh [17], Emory 2024 (5 of 9 eyes) and the base paper's own limitation. The quantitative "~31%" should not be presented as a stable estimate.

- [W7] **MINOR: the emergency-physician sensitivity is not CRAO-specific.** "Emergency physicians reading non-mydriatic photos had 46% sensitivity [23]" sits under "Why CRAO is missed". FOTO-ED II measured sensitivity for *relevant findings in general*, not for CRAO (`research-clinical.md:120`).

- [W8] **MINOR: the photo-quality figure is not CRAO-specific.** "39% of ED CRAO photos were inadequate [16]" (§3 #3). The note reports that colour-photo quality was adequate in 61% across the protocol cohort, not specifically in CRAO eyes (`research-clinical.md:124`). Say "ED eye-stroke photos".

- [W9] **MINOR: some "none exists" statements go further than the notes.**
  - "No published RAO baseline exists [43][45]" for foundation models: the literature note says only "none found in the text I read" (Q4). The brief's own open question 3 admits that RetiZero's supplement was not read.
  - "Only about 151 public RAO images exist": the data note says "about 151" across the sources it checked. ODIR-5K's RAO count is UNVERIFIED, and BRSET has an unsplit `vascular_occlusion` label behind a credentialed data-use agreement.

  Reword both as "found".

- [W10] **MINOR: single-source pillars are not marked as such.** Each of these headline figures comes from one study, and the brief does not say so:
  - New AF "about half within 2 years" [10]: n=100, HR 1.64 vs matched controls, so the controls also had substantial AF.
  - Carotid stenosis ≥70% "in up to 40%" [11]: one prospective cohort. Hayreh reports >50% stenosis in 32%.
  - IRR 44.5 [6]: one Korean self-controlled series, for stroke and heart attack *combined*.
  - Thai DR images rejected at 21% [32]: three Pathum Thani clinics over the first six months.
  - Automation bias 20–46% [46]: mammography, not fundus.

  Add "(one study)" or the n on slides.

- [W11] **MINOR: the AHA caveat is missing from the executive summary.** The executive summary states "AHA 2026 calls IV thrombolysis … 'uncertain' (class 2b) [5]" without the "secondary quote; primary blocked" caveat that §2 and §6 carry.

- [W12] **MINOR: THEIA's p-value looks wrong without context.** "66% vs 48% (p=0.95)" will look like a typo to readers. The p-value comes from the adjusted OR, 1.1 (0.07–18.39), and the percentages use 29 and 27 patients (`research-clinical.md:85`), not the 70 randomised. Add the aOR or the denominators.

- [W13] **MINOR: the camera-gap claim contradicts the brief itself.** "Handheld, smartphone and widefield untested for CRAO [13][14][15]" conflicts with Duan & Tu [13], which did test RAO on ultra-widefield images (18 RAO images, 3 in external test), as the brief says in §6. Say "essentially untested (UWF: 3 external RAO images)".

- [W14] **MINOR: the base paper's selection effects are missing from the gap table.** The base paper removed 88.7% of the CRAO photos (2,538 of 2,861) under its exclusion criteria (`CRAO-AI-detection.md:168`). Many test CRAO photos came from prospective fibrinolysis RCTs (line 201). Both points strengthen the "real-world generalisation" gap, but §1 does not mention them.

- [W15] **MINOR: the Siriraj cohort's usefulness is understated as an unknown.** "Siriraj … acute CRAO cohort … a possible local validation source" leaves out three facts: the cohort is n=49 (17 HBOT vs 32 controls), it covers <24 h (not <4.5 h), and rt-PA patients were excluded (`research-clinical.md:66,138`). Whether it holds any fundus photos is unknown. Open question 2 partly covers this.

- [W16] **MINOR: the LLM claims rest on dated or preprint evidence.**
  - The "multimodal LLMs can't read fundus" evidence [50][51] uses 2024-era models (GPT-4o, Claude 3.5, Gemini 1.5). The CRAO-specific part is ChatGPT-4 on n=12 images.
  - The "LLMs can be persuaded" citation [31] is a 2026 preprint.

  The design choice (no LLM decision) is still sound, but the brief should present it as precaution rather than proof.

- [W17] **MINOR: the prototype environment is not pinned.** The brief quotes exact library versions, but `requirements.txt` lists `torch`, `timm` and `gradio` without versions. The RETFound timing "1.2 h per 1,000 images" is extrapolated from the paper's single statement, "about 1.2 h with a dataset of 1,000 images".

### Questions for authors
- [Q1] Should unknown onset count as "within window" for the normal-photo escalation (the conservative default)?
- [Q2] Should a GCA flag cap the level at URGENT, or swap the stroke-team text for a non-thrombolysis pathway?
- [Q3] Will the Mendeley web-crawled subset be used in any commercial-facing material, given its unclear rights?

### Verdict
The brief is evidence-faithful at the number level and makes no fatal errors. Revision priority is **medium-high**:
- W2 and W3 are safety-relevant mismatches between the brief and `triage.py`, and judges will exercise exactly those paths in the demo script.
- W1 and W5 are pitch-level overstatements that a clinical judge could catch.
- Everything else is wording.

Confidence: high for the claims checked against the notes and the code. Medium for claims that rest on notes I did not re-verify upstream (URLs were not re-fetched, per the scope).

### Revision plan
1. **W2:** in `triage.py:73`, treat `onset is None` as within window, and add an assert for `Case(0.1, 0.9, None)` → ESCALATE. Then align the executive summary with the "<24 h or unknown" rule.
2. **W3:** when `gca_symptoms` is set, do not emit "Activate stroke team … thrombolysis". Use URGENT with a GCA-first action instead, and add an assert on the level and on the absence of thrombolysis text.
3. **W1:** rewrite the comparison as "on a 120-photo subset (30 CRAO) the model found 30/30; three neurologists 50–63.3%".
4. **W4:** restore the third-party-rights caveat for the Mendeley/JSIEC images in §4 and §5.
5. **W5:** change the range to "≈7–32% depending on setting".
6. **W6–W13:** apply the wording fixes listed above: add n's, add "(one study)", change "exists" to "found", add the aOR, and fix the UWF statement.
7. **W14, W15, W17:** add the selection and RCT-sourcing notes to §1, add the Siriraj cohort facts, and pin `requirements.txt`.

---

## Part 2: Inline annotations

> "Its CNN found hyperacute CRAO with AUC 0.96 and sensitivity 92.6% (50 of 54) where three stroke neurologists reached 50–63.3% [1]."

**[W1] MAJOR:** The two figures come from different test sets: 54 CRAO for the model vs a 120-photo, 30-CRAO subset for the neurologists. On the shared subset the model's sensitivity was 100%.

> "(3) a rule that a normal-looking photo never reassures a patient with sudden one-eye vision loss"

**[W2] MAJOR:** `triage.py:73` needs a known onset ≤24 h. With unknown onset or onset >24 h, a low P(CRAO) returns ROUTINE.

> "| 4 | **GCA red-flag branch** → ESR/CRP, steroids, not a lysis candidate | … | Low: built |"

**[W3] MAJOR:** GCA plus high P(CRAO) at ≤4.5 h still returns STROKE_PATHWAY with "Activate stroke team … thrombolysis" listed first. The card contradicts itself.

> "FLAIR (Apache-2.0) plus CC BY datasets is the commercially safer stack"

**[W4] MAJOR:** The data note warns that the Mendeley set's web-crawled and JSIEC images may carry third-party rights. That set is the only RAO source in the recipe.

> "15–32% have acute or silent brain infarcts on MRI [7][8][9]"

**[W5] MAJOR:** The clinical note gives ≈7–32% (Olmsted 6.7%, Emory 18%). The cited studies mix RAO, retinal-ischaemia and MRI-selected CRAO groups.

> "Photos missed ~31% of early ischaemia vs OCT [16]"

**[W6] MAJOR:** This comes from one study with n=16. Give the n, or describe it qualitatively.

> "Emergency physicians reading non-mydriatic photos had 46% sensitivity [23]."

**[W7] MINOR:** This is sensitivity for relevant findings in general, not for CRAO.

> "39% of ED CRAO photos were inadequate [16]"

**[W8] MINOR:** The 61% adequacy figure covers the whole protocol cohort, not just CRAO eyes.

> "no published RAO baseline exists [43][45]"

**[W9] MINOR:** The note says "none found in the text I read", and RetiZero's supplement was not read (open question 3).

> "only about 151 public retinal-artery-occlusion images exist"

**[W9] MINOR:** That count covers the sources checked. ODIR-5K is UNVERIFIED and BRSET's occlusion label is unsplit.

> "New AF is found in about half within 2 years [10], and severe carotid stenosis in up to 40% [11]."

**[W10] MINOR:** Each figure comes from a single study (n=100, HR 1.64 vs controls; one prospective cohort). Mark them as such.

> "AHA 2026 calls IV thrombolysis for CRAO "uncertain" (class 2b) [5]."

**[W11] MINOR:** Add "via secondary source", as §2 already does.

> "THEIA 66% vs 48% (p=0.95)"

**[W12] MINOR:** Add the aOR 1.1 (0.07–18.39) and the 19/29 vs 13/27 denominators. As written, it reads like a typo.

> "Handheld, smartphone and widefield untested for CRAO [13][14][15]"

**[W13] MINOR:** [13] did test RAO on ultra-widefield images (3 external images), as §6 says.

> "| Hyperacute test | 54 CRAO photos (<4.5 h); AUC 0.96, sens 92.6%, spec 85.0% | Small n; every test CRAO had an abnormal fundus |"

**[W14] MINOR:** Also note that 88.7% of the CRAO photos were excluded and many test photos came from RCT cohorts, which suggests selection effects.

> "Siriraj already has a 2003–2022 acute CRAO cohort (HBOT study) [27], a possible local validation source"

**[W15] MINOR:** The cohort is n=49, <24 h, with rt-PA patients excluded, and its photo availability is unknown.

> "On fundus images GPT-4o scored 75%, the others 14–18% [50], and ChatGPT-4 failed on CRAO [51]."

**[W16] MINOR:** These are 2024-era models, and the CRAO evidence is n=12. Frame the "no LLM decision" rule as a precaution.

> "Environment used: Python venv with torch 2.14.1, timm 1.0.30, gradio 6.30.0, opencv 5.0.0"

**[W17] MINOR:** The versions are confirmed in `/tmp/crao-venv`, but `requirements.txt` is unpinned. Pin it.

---

## Checks performed
- Grepped every numeric claim in the executive summary and §1–§6 against the four notes and the base paper. Each number matched unless it is listed above as a weakness.
- Re-ran `python -I triage.py` → "triage self-check OK". Re-ran `python -I vision.py` → "quality good=0.91 blurry=0.03 dark=0.00".
- Probed `triage()` on four extra cases: GCA plus high P(CRAO) at 2 h, low P with unknown onset, low P at 30 h, and low P with no fitting story.
- Not re-run: `train.py` (1 epoch), the Gradio HTTP 200 check, and URL fetches (out of scope).

## Sources
No external URLs were fetched during this verification. Local files inspected:
- `outputs/.drafts/crao-ai-detection-prototype-cited.md`
- `outputs/.drafts/crao-ai-detection-prototype-research-literature.md`
- `outputs/.drafts/crao-ai-detection-prototype-research-clinical.md`
- `outputs/.drafts/crao-ai-detection-prototype-research-data.md`
- `outputs/.drafts/crao-ai-detection-prototype-research-build.md`
- `CRAO-AI-detection.md`
- `experiments/crao-prototype/triage.py`, `vision.py`, `requirements.txt`
