# Tasks: User Profile

- [x] 1. Route
  - [x] 1.1 Create `user` blueprint with `/profile` protected by `login_required`
  - _Requirements: 1_

- [x] 2. Template
  - [x] 2.1 Build `profile.html` glass card with avatar, username, email, provider badge, joined date
  - [x] 2.2 Add `_provider_icon.html` partial (Google, Microsoft, GitHub SVGs)
  - [x] 2.3 Add initials-avatar fallback (server-side and `onerror`)
  - [x] 2.4 Add Explore and Logout buttons
  - _Requirements: 1, 2_

- [x] 3. Navigation
  - [x] 3.1 Show avatar link to `/profile` and Logout in the nav when logged in
  - _Requirements: 2_

- [x] 4. Verification
  - [ ] 4.1 Confirm anonymous redirect and logged-in rendering for each provider
  - [ ] 4.2 Confirm missing avatar and missing email render correctly
  - _Requirements: 1, 3_

- [ ] 5. Confirm the profile with each real OAuth provider after deployment
