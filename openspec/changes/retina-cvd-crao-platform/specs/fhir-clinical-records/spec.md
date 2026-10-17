# Spec Delta

## Purpose

Stores every patient, consent, image, clinical input, AI output and report as standard FHIR R4 resources on an InterSystems IRIS for Health server, so results can move into hospital systems and the demo has one interoperable system of record.

## ADDED Requirements

### Requirement: FHIR server is the system of record
All patient, consent, image, observation, risk, report and audit data SHALL be stored on and read from the configured FHIR R4 server. The application SHALL keep no separate clinical database. Model weights and configuration are not clinical data.

#### Scenario: Data survives app restart
- **WHEN** a case is saved and the application container restarts
- **THEN** the case, images and report are retrieved unchanged from the FHIR server

#### Scenario: FHIR server unavailable
- **WHEN** the FHIR server cannot be reached at start-up or during a save
- **THEN** the application shows "record store unavailable", saves nothing partially, and does not discard the analysis on screen

### Requirement: Resource mapping
The system SHALL map data to FHIR R4 resources: Patient; Consent; Encounter; Media (fundus image and overlays); Observation (vitals, labs, smoking, arcus senilis, vascular measurements, CRAO probability, quality score); Condition (diabetes, hypertension, ASCVD); RiskAssessment (one per equation); DiagnosticReport; Device (model and version); Provenance; AuditEvent.

#### Scenario: Screening case resources
- **WHEN** a Screening-mode case is signed
- **THEN** the server holds an Encounter linking the Media, input Observations, two RiskAssessments (Thai CV Risk and PCE, each naming its method) and a final DiagnosticReport

#### Scenario: Standard codes used
- **WHEN** vital-sign and lab Observations are written
- **THEN** they use LOINC codes (systolic BP 8480-6, diastolic BP 8462-4, total cholesterol 2093-3, HDL 2085-9, LDL 18262-6, smoking status 72166-2)

### Requirement: AI provenance on every output
Every AI-produced resource SHALL reference the Device describing the model name, version and calibration date. A Provenance resource SHALL record whether the agent was the AI device or the signing clinician.

#### Scenario: Override provenance
- **WHEN** a clinician overrides an AI result
- **THEN** the AI Observation keeps its Device reference, and the final DiagnosticReport has a Provenance naming the clinician as author

### Requirement: Report status follows review
The DiagnosticReport status SHALL be "preliminary" before signing and "final" after signing. An amendment after signing SHALL produce status "amended" and keep the prior version.

#### Scenario: Amendment keeps history
- **WHEN** a signed report is amended
- **THEN** the report's status is amended and its previous version stays retrievable through FHIR history

### Requirement: Synthetic Thai demo patients
The system SHALL provide a repeatable seed that loads at least 20 synthetic Thai patients (Thai names, ages 30–79, mixed risk profiles, recent vitals and labs) and SHALL NOT contain any real patient data.

#### Scenario: Seed is repeatable
- **WHEN** the seed runs twice against the same server
- **THEN** the server holds the same 20 synthetic patients without duplicates

### Requirement: Patient search
The clinician SHALL be able to find a patient by name or hospital number and open their prior cases and results.

#### Scenario: Prior results visible
- **WHEN** the clinician opens a seeded patient who has a prior signed screening
- **THEN** the patient view lists the prior case with date, mode and final result
