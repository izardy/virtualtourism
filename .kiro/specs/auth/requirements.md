# Requirements: Authentication (OAuth2)

## Introduction
Users sign in with Google, Microsoft or GitHub. There are no local passwords. First login registers the user automatically.

## Requirements

### Requirement 1: OAuth2 login
**User Story:** As a visitor, I want to log in with an existing account, so that I don't need a new password.

#### Acceptance Criteria
1. The system SHALL offer Google, Microsoft and GitHub login using Authlib.
2. WHEN a login button is clicked THEN the system SHALL redirect to the provider's authorization endpoint with a `state` parameter.
3. WHEN the provider redirects back with a valid code THEN the system SHALL fetch the user info and log the user in with Flask-Login.
4. IF the provider returns an error, the user denies consent, or the state is invalid THEN the system SHALL show a flash error and redirect to the landing page without creating a session.

### Requirement 2: Automatic registration
#### Acceptance Criteria
1. WHEN no user exists with the same `provider` and `provider_id` THEN the system SHALL create a user storing email, username, avatar_url, provider, provider_id and created_at.
2. WHEN the user already exists THEN the system SHALL update username and avatar_url and not create a duplicate.
3. IF the provider gives no email (e.g. private GitHub email) THEN the system SHALL still register the user, using the GitHub `/user/emails` API when permitted, otherwise a null email.

### Requirement 3: Logout
#### Acceptance Criteria
1. WHEN the user selects Logout THEN the system SHALL end the session and redirect to the landing page.

### Requirement 4: Access control
#### Acceptance Criteria
1. Profile and admin routes SHALL require login; unauthenticated users SHALL be redirected to the landing page with a login prompt.
2. Admin routes SHALL additionally require the user to be an admin (email in `ADMIN_EMAILS` env var).

### Requirement 5: Configuration and security
#### Acceptance Criteria
1. Client IDs, secrets and `SECRET_KEY` SHALL be read from environment variables and never committed.
2. Session cookies SHALL be `HttpOnly` and `SameSite=Lax`; `Secure` SHALL be enabled in production.
3. Redirect URIs SHALL be documented in the README for each provider (local and deployed).

## Additional requirements (added during the build)
- WHEN no provider keys are set THEN login buttons for that provider SHALL be hidden, and the demo visitor login SHALL still work (when `DEMO_LOGIN=1`).
- Demo users SHALL be stored with `provider = demo` (or `demo-admin`) so they are never confused with OAuth users.
