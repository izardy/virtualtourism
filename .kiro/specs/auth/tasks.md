# Tasks: Authentication (OAuth2)

- [x] 1. Extensions and config
  - [x] 1.1 Initialize `LoginManager` and Authlib `OAuth` in `app/__init__.py`; add env-driven config and `ProxyFix`
  - [x] 1.2 Add `.env.example` with all provider variables and `ADMIN_EMAILS`
  - _Requirements: 5_

- [x] 2. Provider registration
  - [x] 2.1 Register Google and Microsoft via OIDC discovery metadata
  - [x] 2.2 Register GitHub via explicit OAuth2 endpoints
  - [x] 2.3 Implement `normalize_profile` per provider, including GitHub email fallback
  - _Requirements: 1, 2_

- [x] 3. Auth routes
  - [x] 3.1 Implement `/login/<provider>` (reject unknown providers with 404)
  - [x] 3.2 Implement callback with find-or-create user logic and error handling
  - [x] 3.3 Implement `/logout`
  - _Requirements: 1, 2, 3_

- [x] 4. Access control
  - [x] 4.1 `user_loader` and `unauthorized_handler`
  - [x] 4.2 `admin_required` decorator using `ADMIN_EMAILS`
  - [x] 4.3 Safe `next` redirect validation
  - _Requirements: 4_

- [x] 5. UI
  - [x] 5.1 Provider login buttons partial used on landing page and nav; login/logout state in nav
  - _Requirements: 1, 3_

- [x] 6. Documentation and verification
  - [x] 6.1 README section for registering OAuth apps and redirect URIs (local and deployed)
  - [ ] 6.2 Verify login, repeat login (no duplicate), denied consent and logout for each provider
  - _Requirements: 1-5_

- [x] 7. Demo visitor login and judge admin key (`DEMO_LOGIN`, `DEMO_ADMIN_KEY`)
- [ ] 8. Verify the three OAuth providers with real keys on the production domain
