# Requirements: User Profile

## Introduction
A logged-in user can view a profile page summarizing their account information from the OAuth provider.

## Requirements

### Requirement 1: Profile page
**User Story:** As a logged-in user, I want to see my account details, so that I know which account I'm using.

#### Acceptance Criteria
1. WHEN a logged-in user opens `/profile` THEN the system SHALL display avatar, username, login provider and joined date.
2. IF the user is not logged in THEN the system SHALL redirect to the landing page with a login prompt.
3. IF the user has no avatar_url or it fails to load THEN the system SHALL show a default initials avatar.
4. The joined date SHALL be formatted readably (for example "23 Nov 2026").
5. The provider SHALL be shown with its name and icon (Google, Microsoft or GitHub).

### Requirement 2: Navigation
#### Acceptance Criteria
1. The navigation SHALL show the user's avatar linking to the profile page when logged in, with a Logout option.
2. The profile page SHALL link to Explore and show a Logout button.

### Requirement 3: Privacy
#### Acceptance Criteria
1. The profile page SHALL show only the current user's own data.
2. The email MAY be displayed to the owner but SHALL NOT be exposed on any public page.
