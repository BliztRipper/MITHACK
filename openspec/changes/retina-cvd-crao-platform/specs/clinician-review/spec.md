# Spec Delta

## Purpose

Keeps a human in charge of every AI result. Outputs stay preliminary until a clinician confirms or overrides them, overrides are captured as labelled feedback, and only signed results become final reports.

## ADDED Requirements

### Requirement: AI results are preliminary until signed
Every AI-generated result SHALL be shown and stored with status "preliminary" and the label "AI-assisted, not a diagnosis" until a clinician signs it. Preliminary results SHALL NOT be shown as final in any report or export.

#### Scenario: New result is preliminary
- **WHEN** analysis completes
- **THEN** the result is stored with status preliminary and the view carries the AI-assisted label

### Requirement: Confirm or override with reason
The signing clinician SHALL either confirm the AI finding or override it. An override SHALL require a reason chosen from a fixed list (image misread, clinical findings disagree, poor image, other with free text) and the clinician's own finding.

#### Scenario: Override recorded
- **WHEN** the clinician overrides a "likely CRAO" result with finding "not CRAO" and reason "clinical findings disagree"
- **THEN** the system stores the AI output, the clinician finding, the reason, the clinician identity and the time, and marks the report final with the clinician finding as authoritative

#### Scenario: Override without reason blocked
- **WHEN** the clinician tries to override without choosing a reason
- **THEN** the system blocks signing and asks for a reason

### Requirement: Final clinician report
On signing, the system SHALL produce a final report containing patient identifiers, mode, image with the overlays shown at signing, quality score, AI outputs with model version, risk or triage results, the clinician decision, and the AI-assisted disclosure. It SHALL have a print layout that can be saved as PDF.

#### Scenario: Report printed
- **WHEN** a signed case is opened and the clinician selects "Print report"
- **THEN** a print-ready page with all listed sections opens in the print dialog, from which it can be saved as PDF

### Requirement: Patient-facing summary
The system SHALL offer a short patient-facing summary of the signed result in Thai and in English. It SHALL be built from fixed templates and SHALL contain the next step and when to seek emergency care.

#### Scenario: Thai summary
- **WHEN** the clinician selects the Thai patient summary for a signed Screening-mode case
- **THEN** the system shows a Thai-language summary of the risk band and the agreed next step

### Requirement: Review queue
The system SHALL list cases awaiting signature, with Emergency-mode cases first, then by time waiting. ESCALATE cases SHALL be visible to the ophthalmologist reviewer role.

#### Scenario: Emergency first
- **WHEN** the queue holds a 30-minute-old Screening case and a 2-minute-old Emergency case
- **THEN** the Emergency case is listed first

#### Scenario: Tele-ophthalmology escalation
- **WHEN** a case is triaged ESCALATE
- **THEN** it appears in the ophthalmologist reviewer's queue with the image, overlays and intake answers
