# Spec Delta

## Purpose

Defines how the platform is served on the public internet: where the landing page, web app, API and record store run,
how the browser reaches the API, and the transport, cookie, secret and network protections that hosting requires.

## ADDED Requirements

### Requirement: Public endpoints
The landing page and the clinician web app SHALL each be served at a public HTTPS address. The landing page SHALL link to
the web app. The API SHALL be reachable by browsers only through the web app's own address.

#### Scenario: Landing links to the app
- **WHEN** a visitor opens the landing page
- **THEN** it offers a link to the live demo app and shows the demo accounts

#### Scenario: App and API share an origin
- **WHEN** the web app calls the API
- **THEN** the request goes to a path on the web app's own address, so the session cookie is first-party

### Requirement: Encrypted transport and secure cookies
The system SHALL serve every public address over HTTPS only, and SHALL mark the session cookie `Secure`, `HttpOnly` and
`SameSite=Lax` when hosted.

#### Scenario: Plain HTTP redirected
- **WHEN** a client requests any public address over plain HTTP
- **THEN** it is redirected to HTTPS

#### Scenario: Secure session cookie
- **WHEN** a user signs in on the hosted app
- **THEN** the session cookie carries the `Secure`, `HttpOnly` and `SameSite=Lax` attributes

### Requirement: Private record store
The FHIR record store SHALL NOT be reachable from the public internet. Only the API SHALL reach it, over the host's
private network.

#### Scenario: Store not exposed
- **WHEN** anyone on the internet tries to reach the record store's FHIR endpoint or management portal directly
- **THEN** the connection fails

#### Scenario: API reaches the store
- **WHEN** the hosted API starts
- **THEN** its health endpoint reports the record store as available

### Requirement: Secret handling
Hosted secrets (session signing key, image master key, record-store login) SHALL be supplied
by the hosts' secret stores at run time. They SHALL NOT appear in the repository, in any container image, in build
logs or in responses. The demo account passwords are public by design (see public-demo "Public demo accounts") and
are exempt.

#### Scenario: Image without secrets
- **WHEN** the published container images are inspected
- **THEN** they contain no secret values, no key file and no real patient data

#### Scenario: Missing secret stops start-up
- **WHEN** the hosted API starts without a required secret
- **THEN** it refuses to start and logs which secret name is missing, without printing any value

### Requirement: Reproducible deployment
The deployment SHALL be reproducible from the repository plus the curated demo photos and the hosts' secrets, using
documented commands. The record-store image SHALL be pinned for the host's CPU architecture.

#### Scenario: Redeploy from a clean checkout
- **WHEN** an operator follows the documented deploy steps from a clean checkout with the demo photos and secrets
  available
- **THEN** the landing page, web app, API and record store come up and pass the hosted smoke check

#### Scenario: Hosted smoke check
- **WHEN** the smoke check runs against the public web app
- **THEN** it signs in with a demo account, runs a cached Emergency case to its triage card and confirms the demo banner,
  with no errors
