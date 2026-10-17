# Spec Delta

## Purpose

Estimates a patient's 10-year ASCVD risk with the 2013 ACC/AHA Pooled Cohort Equations, as used by the ACC/AHA ASCVD Risk Estimator Plus. It adds retinal and clinical risk enhancers and suggests guideline-based next steps for a clinician to discuss with the patient.

## ADDED Requirements

### Requirement: Risk factor inputs
Screening mode SHALL collect: age, sex, smoking status, diabetes, systolic and diastolic blood pressure, treatment for hypertension, total cholesterol, HDL cholesterol, optional LDL cholesterol, race group (for PCE only), known atherosclerotic CVD, and arcus senilis (observed by the clinician, yes/no).

#### Scenario: Inputs pre-filled from record
- **WHEN** the patient's record already holds blood pressure or lipid observations from the last 12 months
- **THEN** the form pre-fills them and shows each value's date

#### Scenario: Implausible value rejected
- **WHEN** the clinician enters systolic blood pressure 400 mmHg or total cholesterol 5 mg/dL
- **THEN** the system rejects the value and names the accepted range

### Requirement: Pooled Cohort Equations
The system SHALL compute 10-year ASCVD risk with the 2013 ACC/AHA Pooled Cohort Equations for ages 40 to 79. Patients not recorded as African American SHALL use the white equations, and the result SHALL carry a note that PCE was not derived in Asian populations and may overestimate risk.

#### Scenario: PCE computed with caveat
- **WHEN** a 60-year-old Thai patient with complete inputs is assessed
- **THEN** the system shows the PCE 10-year risk with the population caveat

#### Scenario: PCE reference case
- **WHEN** the inputs match the published 2013 ACC/AHA worked example for a white woman
- **THEN** the computed risk matches the published value to within 0.1 percentage point

#### Scenario: Out of validated age
- **WHEN** the patient is 35 or 82 years old
- **THEN** the system shows "outside validated age range (40–79)" instead of a PCE risk number

### Requirement: Calculator bypass for statin benefit groups
The system SHALL NOT present a primary-prevention risk number as the basis for treatment when the patient is in a 2018 AHA/ACC statin benefit group: known atherosclerotic CVD, LDL cholesterol of 190 mg/dL or higher, or diabetes mellitus at age 40 to 75 with LDL cholesterol of 70 mg/dL or higher. It SHALL instead state the applicable statin benefit group.

#### Scenario: Known ASCVD
- **WHEN** the patient is recorded as having known atherosclerotic CVD
- **THEN** the system states "secondary prevention: risk calculators do not apply" and shows no primary-prevention suggestion

#### Scenario: Severe hypercholesterolaemia
- **WHEN** LDL cholesterol is 190 mg/dL or higher
- **THEN** the system states that high-intensity statin is indicated regardless of calculated risk

#### Scenario: Diabetes aged 40–75
- **WHEN** a 55-year-old patient with diabetes has LDL cholesterol of 120 mg/dL
- **THEN** the system states "diabetes 40–75: moderate-intensity statin indicated regardless of calculated risk", and any PCE number shown is labelled as informing statin intensity only

### Requirement: Risk categories and management suggestions
The system SHALL map PCE risk to the ACC/AHA bands (<5%, 5 to <7.5%, 7.5 to <20%, 20% or higher). It SHALL show the matching suggestion text, labelled "for clinician–patient discussion".

#### Scenario: High PCE band
- **WHEN** PCE risk is 22%
- **THEN** the suggestion is to consider high-intensity statin to lower LDL-C by at least 50%, with lipid reassessment 4–12 weeks after starting

#### Scenario: Low PCE band
- **WHEN** PCE risk is 3%
- **THEN** the suggestion emphasises lifestyle change and reassessment of risk factors every 4–6 years

#### Scenario: Stage 1 hypertension
- **WHEN** blood pressure is 130–139 / 80–89 mmHg
- **THEN** the system labels stage 1 hypertension and states whether 10-year risk is below 10% or 10% and above

### Requirement: Risk enhancers
The system SHALL list risk enhancers that apply. These are retinal vascular measurements outside reference (from retinal-image-analysis) and clinical enhancers entered by the clinician. Enhancers SHALL NOT change the calculated risk number. Retinal enhancers SHALL be labelled "investigational, not a guideline-listed risk enhancer".

#### Scenario: Borderline risk with retinal enhancer
- **WHEN** PCE risk is 6% and the artery-to-vein ratio is outside reference
- **THEN** the system lists "retinal arteriolar narrowing (investigational)" as a risk enhancer, notes that enhancers favour statin discussion in the 5–7.5% band, and leaves the 6% value unchanged

#### Scenario: Retinal measurement unavailable
- **WHEN** the image failed the quality gate
- **THEN** the risk is still computed from clinical inputs and the report states that retinal enhancers were not assessed

### Requirement: Arcus senilis prompt
When arcus senilis is recorded, the system SHALL show it as a clinical observation rather than an equation input. Under age 45 it SHALL prompt a lipid check and consideration of familial hypercholesterolaemia.

#### Scenario: Arcus in a young patient
- **WHEN** arcus senilis is recorded for a 38-year-old
- **THEN** the system prompts "check lipid profile; consider familial hypercholesterolaemia" and does not alter the risk number
