# Spec Delta

## Purpose

Protects patients' retinal images, which are biometric data, and their health records under Thai PDPA. Covers authenticated role-based access, encryption, purpose-limited consent, an audit trail of every access, and erasure on consent withdrawal.

## ADDED Requirements

### Requirement: Authenticated access
Every page and API endpoint other than login and health check SHALL require an authenticated user. Sessions SHALL expire after 30 minutes of inactivity.

#### Scenario: Unauthenticated request refused
- **WHEN** a request without a valid session asks for a patient record or image
- **THEN** the system responds 401 and returns no patient data

#### Scenario: Idle session expires
- **WHEN** a signed-in user is inactive for 30 minutes
- **THEN** the next request requires signing in again

### Requirement: Role-based permissions
The system SHALL support three roles. Frontline clinicians capture, analyse and sign their own cases. Ophthalmologist reviewers read and sign escalated cases. Administrators view monitoring and audit data but cannot open patient images.

#### Scenario: Admin cannot view images
- **WHEN** an administrator requests a fundus image
- **THEN** the system responds 403

#### Scenario: Reviewer sees escalated cases
- **WHEN** an ophthalmologist reviewer opens an ESCALATE case from another clinician
- **THEN** the system shows the case and lets the reviewer sign it

### Requirement: Encryption of retinal images
Fundus images and their overlays SHALL be encrypted before they reach the record store and decrypted only for an authorised viewer. Images SHALL never appear in application logs, error messages or analytics.

#### Scenario: Stored image unreadable without key
- **WHEN** the stored image payload is read directly from the record store without the application key
- **THEN** it is not a decodable image

#### Scenario: No images in logs
- **WHEN** analysis fails with an exception
- **THEN** the log entry contains the case identifier and error, and no image bytes or patient names

### Requirement: Purpose-limited consent
Consent SHALL record separate purposes: care (required to process the image) and model improvement (optional). A case SHALL be exported for retraining only if model-improvement consent is active.

#### Scenario: No training consent
- **WHEN** reviewed cases are exported for retraining and a patient gave care consent only
- **THEN** that patient's cases are excluded from the export

### Requirement: Consent withdrawal and erasure
When a patient withdraws consent, the system SHALL delete their fundus images and overlays. It SHALL keep the signed clinical report text, which may be legally required medical record content, with the image references removed. It SHALL record the withdrawal.

#### Scenario: Withdrawal erases images
- **WHEN** an authorised clinician records consent withdrawal for a patient
- **THEN** that patient's images and overlays can no longer be retrieved, their signed reports remain without images, and the Consent status becomes inactive

### Requirement: Access audit trail
The system SHALL write an audit event for every view, create, update, export and delete of patient data and images. Each event SHALL record user, role, action, resource, time and outcome. Audit events SHALL be append-only for all roles.

#### Scenario: Image view audited
- **WHEN** a clinician opens a case image
- **THEN** an audit event records the clinician, the image resource, action "read" and the time

#### Scenario: Audit cannot be edited
- **WHEN** any user tries to change or delete an audit event through the application
- **THEN** the system refuses
