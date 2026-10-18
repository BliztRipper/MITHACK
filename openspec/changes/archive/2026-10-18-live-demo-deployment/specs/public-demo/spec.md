# Spec Delta

## Purpose

Defines how the platform behaves when it runs as a public demonstration on the internet: only curated demo inputs,
only synthetic records, visible demo labelling, public demo accounts, regular resets and abuse limits.

## ADDED Requirements

### Requirement: Demo mode switch
The system SHALL run in demo mode when the deployment enables it, and SHALL apply every requirement in this capability
only in demo mode. Outside demo mode the system SHALL behave exactly as before.

#### Scenario: Local run unchanged
- **WHEN** the system runs without demo mode enabled
- **THEN** uploads of any fundus photo are analysed as before and no demo banner is shown

#### Scenario: Health reports the mode
- **WHEN** a client requests the health endpoint in demo mode
- **THEN** the response states that demo mode is on

### Requirement: Curated demo inputs only
In demo mode the system SHALL analyse only the curated demo photos whose licences permit public redistribution. It SHALL
refuse any other upload before storing or processing it, and SHALL tell the user to pick one of the demo photos.

#### Scenario: Curated photo accepted
- **WHEN** a clinician starts a case with one of the curated demo photos
- **THEN** the system returns the precomputed result for that photo within 2 seconds

#### Scenario: Other photo refused
- **WHEN** a clinician uploads any photo that is not one of the curated demo photos
- **THEN** the system refuses it with a message to use a demo photo, and stores no image, record or audit entry
  containing the photo

#### Scenario: Demo photos offered with credits
- **WHEN** a clinician opens the photo step of a new case
- **THEN** the system offers every curated demo photo by name, each with its source and licence

### Requirement: Synthetic data only
In demo mode every patient record SHALL be synthetic. The system SHALL NOT offer patient creation or import, and SHALL
state on every page that the data is synthetic.

#### Scenario: Persistent demo banner
- **WHEN** any page of the web app is shown in demo mode
- **THEN** a banner states "Demo: synthetic patients, not a medical device, data resets daily" and stays visible while
  scrolling

#### Scenario: No patient creation
- **WHEN** a user looks for a way to add or import a patient in demo mode
- **THEN** no such action exists

### Requirement: Scheduled reset
The record store SHALL be reset to the 20 synthetic seed patients, with no cases, consents or images, at least once a day
and whenever the record store restarts. Each reset SHALL also discard all image keys and withdrawal markers.

#### Scenario: Daily reset
- **WHEN** a day has passed since the last reset
- **THEN** the store holds exactly the 20 seed patients and their seeded prior reports, and no other case data

#### Scenario: Reset after restart
- **WHEN** the record store restarts for any reason
- **THEN** it comes back seeded before the API accepts patient requests, and a patient withdrawn before the restart can
  consent again

### Requirement: Public demo accounts
In demo mode the system SHALL provide one account for each role (frontline GP, ophthalmologist reviewer, administrator)
whose credentials are published on the landing page and the login screen. These accounts SHALL exist only in demo mode.

#### Scenario: Credentials shown at login
- **WHEN** a visitor opens the login screen in demo mode
- **THEN** the screen lists the three demo accounts, their roles and their passwords

#### Scenario: Demo accounts absent outside demo mode
- **WHEN** the system runs without demo mode
- **THEN** the published demo credentials do not sign in

### Requirement: Abuse limits
In demo mode the system SHALL limit each client to a fixed number of sign-in attempts and case creations per period,
and SHALL tell the client when it must wait.

#### Scenario: Too many sign-in attempts
- **WHEN** a client makes more than 10 failed sign-in attempts within 10 minutes
- **THEN** further attempts are refused for the rest of the period with a "try again later" message

#### Scenario: Too many cases
- **WHEN** a client creates more than 30 cases within an hour
- **THEN** further case creation is refused for the rest of the hour with a "try again later" message
