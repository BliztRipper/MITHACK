# Spec Delta

## Purpose

Turns the CRAO probability, image quality, onset time and red-flag symptoms into a triage level and an ordered action list, using readable deterministic rules, so a non-ophthalmologist knows what to do next for sudden vision loss.

## ADDED Requirements

### Requirement: Deterministic triage levels
The system SHALL assign exactly one triage level per Emergency-mode case: STROKE_PATHWAY, URGENT, ESCALATE, RETAKE or ROUTINE. It SHALL use fixed rules over calibrated probability, quality score, hours since onset, symptom answers and GCA symptoms. The same inputs SHALL always give the same level and actions.

#### Scenario: Likely CRAO within 4.5 hours
- **WHEN** probability is in the "likely" band, quality passes, onset is 2 hours and there are no GCA symptoms
- **THEN** the level is STROKE_PATHWAY and the first action is to activate the stroke team, stating that thrombolysis benefit for CRAO is uncertain and the decision follows local protocol

#### Scenario: Likely CRAO beyond 4.5 hours or unknown onset
- **WHEN** probability is "likely" and onset is 10 hours or unknown
- **THEN** the level is URGENT with same-day stroke work-up (brain MRI, carotid imaging, ECG/AF monitoring, echocardiography), and for unknown onset the reasons ask for last-known-well time

#### Scenario: Uncertain probability
- **WHEN** probability is in the "uncertain" band
- **THEN** the level is ESCALATE with urgent tele-ophthalmology review (OCT if available)

### Requirement: Normal-looking photo does not reassure
When probability is "unlikely" but the patient reports sudden painless one-eye vision loss with onset within 24 hours or unknown, the system SHALL assign ESCALATE, because early CRAO can show a near-normal fundus.

#### Scenario: Fitting story, normal photo
- **WHEN** probability is "unlikely", onset is 2 hours and the loss was sudden, painless and in one eye
- **THEN** the level is ESCALATE with the action "early CRAO can have a normal fundus, refer urgently"

#### Scenario: Old complaint, normal photo
- **WHEN** probability is "unlikely" and onset is 72 hours
- **THEN** the level is ROUTINE with routine ophthalmology referral

#### Scenario: Story does not fit
- **WHEN** probability is "unlikely", onset is unknown, and the loss was not sudden, painless and monocular
- **THEN** the level is ROUTINE

### Requirement: Quality gate overrides the model
When the image fails the quality gate, the system SHALL assign RETAKE whatever the model output. In Emergency mode it SHALL also state that if a gradable photo cannot be obtained within minutes, the patient must be referred urgently, not delayed.

#### Scenario: Poor image with high probability
- **WHEN** quality is below threshold and probability would be 0.9
- **THEN** the level is RETAKE and the actions include the urgent-referral fallback

### Requirement: Giant cell arteritis branch
When GCA symptoms are reported, the system SHALL put the arteritis action first (urgent ESR/CRP, steroids per protocol, not a thrombolysis candidate). It SHALL NOT show the stroke-team activation card, whatever the image or quality.

#### Scenario: GCA with likely CRAO
- **WHEN** GCA symptoms are reported, probability is "likely" and onset is 2 hours
- **THEN** the level is URGENT, the first action is the arteritis action, and no action activates the stroke team

#### Scenario: GCA with poor image
- **WHEN** GCA symptoms are reported and the image fails quality
- **THEN** the level is RETAKE and the arteritis action is still listed

### Requirement: Secondary prevention reminder
For STROKE_PATHWAY and URGENT cases the system SHALL append a secondary-prevention action: antiplatelet and statin decision, blood pressure and glucose control, and AF screening.

#### Scenario: Reminder appended
- **WHEN** the level is URGENT
- **THEN** the last action is the secondary-prevention reminder

### Requirement: Reasons shown with every level
Every triage result SHALL list the rule inputs that produced it (probability and band, quality, onset, symptoms) so the clinician can see why the level was chosen.

#### Scenario: Reasons listed
- **WHEN** any triage card is displayed
- **THEN** it shows the triggering reasons, for example "p=0.82 ≥ 0.70" and "onset 2.0 h ≤ 4.5 h"

### Requirement: Configurable thresholds
The probability thresholds, quality threshold, hyperacute window (4.5 h) and acute window (24 h) SHALL be configuration values, displayed in the about panel and marked "placeholder, not clinically validated" until set on a held-out set.

#### Scenario: Thresholds visible
- **WHEN** the clinician opens the about panel
- **THEN** the current threshold values and their validation status are displayed
