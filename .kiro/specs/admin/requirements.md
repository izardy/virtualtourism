# Requirements: Admin Panel

## Introduction
A lightweight admin panel (`admin.html`) lets authorized users manage destinations, hotspots and uploaded media without touching the database or filesystem directly.

## Requirements

### Requirement 1: Access
**User Story:** As an administrator, I want a protected panel, so that only trusted users can change content.

#### Acceptance Criteria
1. WHEN a non-logged-in user requests `/admin` THEN the system SHALL redirect to the landing page.
2. IF a logged-in user is not an admin THEN the system SHALL return 403.
3. Admins SHALL be identified by email listed in the `ADMIN_EMAILS` environment variable.

### Requirement 2: Destinations
#### Acceptance Criteria
1. The admin SHALL be able to add a destination (name, description, location, category).
2. The admin SHALL be able to edit a destination's fields, including its description.
3. The admin SHALL be able to delete a destination after a confirmation; its hotspots SHALL be deleted too.
4. WHEN the name is empty THEN the system SHALL reject the form with a validation message.

### Requirement 3: Media uploads
#### Acceptance Criteria
1. The admin SHALL be able to upload a GLB model, thumbnail, hero image, hotspot images and audio narrations.
2. The system SHALL accept only allowed extensions: `.glb`/`.gltf` for models, `.jpg/.jpeg/.png/.webp` for images, `.mp3/.ogg/.wav/.m4a` for audio.
3. The system SHALL enforce size limits (models 50 MB, images 5 MB, audio 20 MB) and show an error when exceeded.
4. The system SHALL store files under `static/models`, `static/images`, `static/audio` with sanitized, unique filenames and save the relative path in the database.

### Requirement 4: Hotspots
#### Acceptance Criteria
1. The admin SHALL be able to create, edit and delete hotspots for a destination with title, description, x/y/z position, image and audio.
2. WHEN coordinates are not numeric THEN the system SHALL reject the form.
3. The admin SHALL be able to pick coordinates by clicking in a preview of the 3D model (nice-to-have; manual entry is required).

### Requirement 5: Safety
#### Acceptance Criteria
1. All state-changing admin requests SHALL include a CSRF token.
2. WHEN a file is replaced or its record deleted THEN the system SHALL remove the old file if unused elsewhere.
