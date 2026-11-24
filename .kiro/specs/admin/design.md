# Design: Admin Panel

## Overview
Server-rendered admin at `/admin` in blueprint `admin`, protected by `@login_required` and `@admin_required` (see auth spec). One page with two tabs (Destinations, Hotspots) built with Tailwind and small amounts of JavaScript. Forms use `multipart/form-data` and post to dedicated endpoints, then redirect with a flash message.

## Routes
| Route | Method | Action |
|---|---|---|
| `/admin` | GET | Dashboard listing destinations and hotspots |
| `/admin/destinations` | POST | Create destination |
| `/admin/destinations/<id>` | POST | Update destination (fields and files) |
| `/admin/destinations/<id>/delete` | POST | Delete destination |
| `/admin/destinations/<id>/hotspots` | POST | Create hotspot |
| `/admin/hotspots/<id>` | POST | Update hotspot |
| `/admin/hotspots/<id>/delete` | POST | Delete hotspot |

## Upload service (`app/services/uploads.py`)
`save_upload(file, kind)`:
1. Check `kind` in `{model, image, audio}` and extension against the allowlist.
2. Sanitize with `secure_filename`, prefix with a short UUID to avoid collisions.
3. Save to `static/<models|images|audio>/` and return the path relative to `static/`.
`delete_upload(path)` removes the file only if no destination or hotspot still references it.
`MAX_CONTENT_LENGTH` is set to 60 MB; per-kind limits are checked using file size after save-stream measurement. Oversize returns a validation error.

## UI
- Destination list with Add/Edit/Delete; edit form with text fields and file inputs for model, thumbnail and hero image, showing the current file name.
- Hotspot table per destination with inline edit form: title, description textarea, x/y/z number inputs, image and audio inputs.
- Optional: "Pick position" button opening a small Three.js preview that fills x/y/z from a raycast click, reusing `ModelLoader`.
- Styling follows the ui spec (dark glass cards).

## Validation and errors
Server-side validation in each handler: required name/title, float parsing for coordinates, upload checks. On error, re-render the form with messages and 400 status; on success redirect (PRG pattern) with a flash.

## Security
- CSRF: Flask-WTF `CSRFProtect` (or a session token checked in handlers); the hidden token field is in every form.
- Admin check on every route, not just the dashboard.
- Uploads are never executed; only served from static; filenames sanitized; extension allowlist.
- Delete endpoints are POST only.

## Testing
Manual: add destination with GLB, add hotspot with image/audio, view it in the viewer. Optional tests for non-admin 403 and bad extension rejection.

## As built
- CSRF uses a per-session token (`session["_csrf"]`) checked in `before_request` for every POST; Flask-WTF was not needed.
- Hotspot coordinates use glTF axes (x east, y up, z south). The form says so.
- `delete_upload` only removes files with an 8-character hex prefix (admin uploads), never the bundled seed assets, and only when no record still uses them.
- Tested with the Flask test client: non-admin 403, missing token 400, bad extension and non-numeric coordinate rejected, create and cascade delete clean up files. Not tested: uploading a real GLB and viewing it.
- Optional 3D coordinate picker was not built.
