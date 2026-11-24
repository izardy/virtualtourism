# Design: Authentication (OAuth2)

## Overview
Authlib's Flask integration registers three providers on a shared `OAuth` object. A single normalizing function converts each provider's profile into a common structure used to find or create a `User`.

## Components
- `app/routes/auth.py` blueprint `auth`:
  - `GET /login/<provider>`: `oauth.<provider>.authorize_redirect(url_for('auth.callback', provider=provider, _external=True))`
  - `GET /auth/<provider>/callback`: `authorize_access_token()`, fetch profile, normalize, upsert, `login_user`
  - `GET /logout`: `logout_user()`
- `app/auth_providers.py`: provider registration and `normalize_profile(provider, token, client)`.
- `login_manager.user_loader` loads by id; `unauthorized_handler` redirects to `/` with a flash message.
- `admin_required` decorator checks `current_user.email in ADMIN_EMAILS`.

## Provider configuration
| Provider | Method | Scopes | Profile source |
|---|---|---|---|
| Google | OIDC discovery (`accounts.google.com/.well-known/openid-configuration`) | `openid email profile` | ID token / userinfo: `sub`, `email`, `name`, `picture` |
| Microsoft | OIDC discovery (`login.microsoftonline.com/common/v2.0/.well-known/openid-configuration`) | `openid email profile` | ID token: `sub`/`oid`, `email` or `preferred_username`, `name`; avatar via Graph `/me/photo` optional, else generated initials avatar |
| GitHub | OAuth2 (`github.com/login/oauth/*`, API `api.github.com`) | `read:user user:email` | `/user`: `id`, `login`, `avatar_url`, `email`; fallback `/user/emails` primary verified |

Microsoft uses the `common` tenant with `iss` validation relaxed as required for multi-tenant.

## Normalized profile
```
{ provider, provider_id (str), email, username, avatar_url }
```

## Flow
1. User clicks provider button -> `/login/<provider>`.
2. Authlib stores `state` in session and redirects to provider.
3. Callback validates state, exchanges code, fetches profile.
4. Upsert on `(provider, provider_id)` and `login_user(user)`.
5. Redirect to `next` (validated as a relative path) or `/profile`.

## Error handling
Wrap callback in try/except for `OAuthError` and network errors; flash "Login failed, please try again" and redirect to `/`. Log details server-side without tokens.

## Security
- Unique constraint on `(provider, provider_id)`.
- `next` parameter limited to same-origin relative paths.
- Secrets from env: `GOOGLE_CLIENT_ID/SECRET`, `MICROSOFT_CLIENT_ID/SECRET`, `GITHUB_CLIENT_ID/SECRET`, `SECRET_KEY`, `ADMIN_EMAILS`.
- Behind a proxy (Render/Railway) use `ProxyFix` so `_external` URLs use https.
- Local dev may use `AUTHLIB_INSECURE_TRANSPORT=1` only when `FLASK_ENV=development`.

## Testing
Mock `normalize_profile` to test upsert and duplicate handling; manual login test per provider.

## As built
- `app/auth_providers.py` registers a provider only when both id and secret exist (`ENABLED_PROVIDERS`); `normalize_profile` returns `{provider_id, email, username, avatar_url}`.
- Microsoft uses the `common` tenant; the callback passes `claims_options={"iss": {"essential": False}}` because the multi-tenant issuer contains a `{tenantid}` placeholder. Untested with real credentials.
- GitHub: `read:user user:email`, with `/user/emails` fallback for a private email.
- `next` redirects are restricted to same-site relative paths.
- Demo access: `/login-demo` (normal user) and `/login-demo-admin?key=...` (admin, only when `DEMO_ADMIN_KEY` is set). Admin check: `ADMIN_EMAILS`, or provider `demo-admin` with a configured key.
- `ProxyFix` is applied so OAuth redirect URIs use https behind a proxy; set `COOKIE_SECURE=1` in production.
- Status: demo login, logout, 403 for non-admins and redirects were tested; Google, Microsoft and GitHub flows were not exercised (no credentials).
