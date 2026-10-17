# Spec Delta

## Purpose

Shows whether the deployed model is still working safely. Tracks quality, abstention, clinician agreement and calibration on reviewed cases, raises drift alerts, and feeds consented, reviewed cases into offline retraining of a locked, versioned model.

## ADDED Requirements

### Requirement: Monitoring dashboard
The system SHALL show administrators and reviewers, per model version and for a selectable period: case count by mode, quality-gate rejection rate, uncertain-band rate, clinician agreement rate, override reasons, and triage level distribution.

#### Scenario: Metrics shown per version
- **WHEN** an administrator opens the dashboard for the last 30 days
- **THEN** each metric is shown per model version with the number of cases it is based on

### Requirement: Calibration on reviewed cases
The dashboard SHALL show a reliability summary that compares predicted probability bands with clinician-confirmed findings on signed Emergency-mode cases. When fewer than 30 signed cases exist, it SHALL show "insufficient data" instead of the summary.

#### Scenario: Too few cases
- **WHEN** only 12 signed Emergency-mode cases exist for the current version
- **THEN** the calibration panel shows "insufficient data (12 of 30)"

### Requirement: Drift alerts
The system SHALL raise a visible alert when, over a rolling window of the last 50 cases, the quality rejection rate, uncertain-band rate or override rate exceeds its configured limit, or the agreement rate exceeds an upper limit (a sign of rubber-stamping). The alert SHALL stay until an administrator acknowledges it with a note.

#### Scenario: Override spike
- **WHEN** 15 of the last 50 signed cases were overrides and the limit is 20%
- **THEN** the dashboard shows an override-rate alert and logs it

#### Scenario: Possible rubber-stamping
- **WHEN** 50 of the last 50 signed cases were confirmed unchanged and the agreement upper limit is 98%
- **THEN** the dashboard shows an agreement-rate alert suggesting automation bias review

### Requirement: Locked, versioned model
The deployed model SHALL NOT learn from cases at runtime. A new model version SHALL be deployed only with a recorded version identifier, training-data description, validation results and calibration date. All new results SHALL reference that version.

#### Scenario: Version switch recorded
- **WHEN** a new model version is deployed
- **THEN** results produced after deployment reference the new version, and results produced before keep the old one

### Requirement: Reviewed-case export for retraining
Administrators SHALL be able to export signed cases with model-improvement consent as a de-identified dataset. Each entry SHALL hold the image, the clinician's final finding as label, the AI output and the model version, with direct identifiers removed.

#### Scenario: De-identified export
- **WHEN** an administrator exports reviewed cases
- **THEN** the export holds only consented cases, contains no names, hospital numbers or dates of birth, and is logged as an audit event

### Requirement: Incident reporting
Any clinician SHALL be able to flag a case as a suspected AI safety incident with a description. Flagged cases SHALL appear on the dashboard until an administrator closes them.

#### Scenario: Incident flagged
- **WHEN** a clinician flags a signed case as "missed CRAO later confirmed"
- **THEN** the case appears in the dashboard's open incidents list with the description
