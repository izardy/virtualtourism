# Requirements: Database and Seed Data

## Introduction
SQLite database `virtualtourism.db` accessed through Flask-SQLAlchemy, holding users, destinations and hotspots, with Muzium Perang Penang preloaded.

## Requirements

### Requirement 1: Schema
**User Story:** As a developer, I want a simple schema, so that the app and admin panel can share it.

#### Acceptance Criteria
1. The system SHALL define `users` (id, email, username, avatar_url, provider, provider_id, created_at).
2. The system SHALL define `destinations` (id, name, description, location, category, thumbnail, hero_image, model_path).
3. The system SHALL define `hotspots` (id, destination_id, title, description, x_position, y_position, z_position, image_path, audio_path).
4. `hotspots.destination_id` SHALL be a foreign key to `destinations.id`; deleting a destination SHALL delete its hotspots.
5. `(provider, provider_id)` SHALL be unique on `users`.

### Requirement 2: Initialization
#### Acceptance Criteria
1. WHEN the app starts and tables do not exist THEN the system SHALL create them automatically in `virtualtourism.db`.
2. IF the database file already exists THEN the system SHALL keep existing data.

### Requirement 3: Seed data
#### Acceptance Criteria
1. WHEN the destinations table is empty THEN the system SHALL insert Muzium Perang Penang with its profile and 10 hotspots.
2. The seed SHALL be idempotent: running it again SHALL NOT create duplicates.

### Requirement 4: Integrity
#### Acceptance Criteria
1. Required fields (`destinations.name`, `hotspots.title`, `hotspots.destination_id`, `users.provider`, `users.provider_id`) SHALL be non-null.
2. Hotspot coordinates SHALL default to 0.0 when omitted.
