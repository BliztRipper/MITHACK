# Spec Delta

## Purpose

Lets a frontline clinician capture a consented colour fundus photograph for a patient in screening or emergency mode, and rejects images too poor to read before any model sees them.

## ADDED Requirements

### Requirement: Mode selection before capture
The system SHALL require the clinician to choose either Screening mode (CVD risk) or Emergency mode (sudden vision loss / suspected CRAO) before uploading an image. The chosen mode SHALL decide which clinical inputs are requested and which analysis runs.

#### Scenario: Emergency mode requests onset and symptoms
- **WHEN** the clinician selects Emergency mode
- **THEN** the system asks for hours since vision loss (or "unknown"), whether the loss was sudden, painless and in one eye, and giant cell arteritis symptoms (age over 50 with headache, jaw claudication or scalp tenderness)

#### Scenario: Screening mode requests risk factors
- **WHEN** the clinician selects Screening mode
- **THEN** the system asks for the risk factors defined in the cvd-risk-assessment capability, pre-filled from the patient's existing record where available

### Requirement: Consent gate for biometric capture
The system SHALL NOT accept an image upload for a patient who has no active consent for retinal image processing. Retinal images are biometric and health data under Thai PDPA section 26, so explicit consent is required.

#### Scenario: Upload blocked without consent
- **WHEN** a clinician tries to upload an image for a patient with no active consent
- **THEN** the system blocks the upload and shows the consent form instead

#### Scenario: Consent recorded then upload allowed
- **WHEN** the clinician records the patient's explicit consent (purpose, retention period, right to withdraw) and then uploads
- **THEN** the system stores the consent with timestamp and recorder, and accepts the upload

### Requirement: Accepted image formats and size
The system SHALL accept JPEG and PNG fundus images up to 20 MB and SHALL reject other formats or larger files with a clear message.

#### Scenario: Unsupported file rejected
- **WHEN** the clinician uploads a PDF or a 30 MB file
- **THEN** the system rejects it, names the reason, and stores nothing

### Requirement: Metadata stripping
The system SHALL remove embedded metadata (EXIF, GPS, device serials) from every accepted image before storing or analysing it.

#### Scenario: EXIF removed
- **WHEN** an image containing EXIF and GPS tags is accepted
- **THEN** the stored image contains no EXIF or GPS tags

### Requirement: Image quality gate
The system SHALL score every accepted image for gradability before any disease model runs. An image below the quality threshold SHALL NOT be analysed, and the clinician SHALL see a specific retake reason.

#### Scenario: Poor image refused with reason
- **WHEN** an uploaded image is too dark, blurred or shows too little retinal field
- **THEN** the system shows "Retake" with the failing check (for example "underexposed: dilate pupil and increase flash") and runs no disease model

#### Scenario: Gradable image passes
- **WHEN** an uploaded image passes the quality threshold
- **THEN** the system shows its quality score and continues to analysis

#### Scenario: Non-fundus image refused
- **WHEN** the uploaded image is not a fundus photograph (for example a face or a document)
- **THEN** the quality gate refuses it as "not a fundus image"
