# Tasks: Database and Seed Data

- [x] 1. Database setup
  - [x] 1.1 Create `db = SQLAlchemy()` and configure `SQLALCHEMY_DATABASE_URI` (default `sqlite:///virtualtourism.db`)
  - [x] 1.2 Add SQLite `PRAGMA foreign_keys=ON` listener
  - _Requirements: 2_

- [x] 2. Models
  - [x] 2.1 `User` model with unique `(provider, provider_id)`
  - [x] 2.2 `Destination` model with hotspot relationship and cascade
  - [x] 2.3 `Hotspot` model with coordinate defaults
  - [x] 2.4 `to_dict()` helpers (hotspot splits description and facts)
  - _Requirements: 1, 4_

- [x] 3. Initialization and seeding
  - [x] 3.1 Call `db.create_all()` in `create_app`
  - [x] 3.2 Implement `seed_if_empty()` with Muzium Perang Penang and 10 hotspots from `seed_data.py`
  - [x] 3.3 Wire seed into app startup with rollback and logging on failure
  - _Requirements: 2, 3_

- [x] 4. Verification
  - [x] 4.1 Start the app twice and confirm 1 destination and 10 hotspots
  - [x] 4.2 Confirm deleting a destination removes its hotspots
  - _Requirements: 1, 3_
