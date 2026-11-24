# Design: User Profile

## Overview
A single read-only page rendered from `current_user`, in blueprint `user`.

## Route
| Route | Method | Behavior |
|---|---|---|
| `/profile` | GET | `@login_required`; renders `profile.html` with `current_user` |

Unauthenticated access is handled by the login manager's `unauthorized_handler` (redirect to `/` with a flash message), defined in the auth spec.

## Template (`profile.html`)
Extends `base.html`; a centered glass card containing:
- Avatar (`<img>` 112 px round with cyan ring). `onerror` swaps to an initials avatar; when `avatar_url` is empty, the initials avatar is rendered server-side (first letter of username on a navy/cyan gradient).
- Username (heading).
- Email (muted text, if present).
- Provider badge: icon and capitalized provider name.
- Joined date: `{{ user.created_at.strftime('%d %b %Y') }}`.
- Buttons: "Explore destinations" (primary), "Logout" (glass).

## Data
Uses the `users` table only; no new fields. Provider icons are inline SVGs in a partial `_provider_icon.html`.

## Security
- The page only reads `current_user`; no user id is accepted in the URL, which prevents viewing other profiles.
- Avatar URLs are rendered through Jinja autoescaping; `referrerpolicy="no-referrer"` is set on the image.

## Testing
Manual: log in with each provider and check the details; open `/profile` when logged out and confirm the redirect. Optional test client check for 302 when anonymous and 200 when logged in.
