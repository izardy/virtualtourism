# Design: Database and Seed Data

## Overview
Three SQLAlchemy models in `app/models/`, one shared `db = SQLAlchemy()` instance. Tables are created with `db.create_all()` at startup (no migrations for the MVP).

## Models
```python
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = Integer PK
    email = String(255), nullable
    username = String(120), not null
    avatar_url = String(500)
    provider = String(20), not null          # google | microsoft | github
    provider_id = String(255), not null
    created_at = DateTime, default=datetime.utcnow
    __table_args__ = (UniqueConstraint("provider", "provider_id"),)

class Destination(db.Model):
    __tablename__ = "destinations"
    id, name (not null), description (Text), location, category,
    thumbnail, hero_image, model_path
    hotspots = relationship("Hotspot", backref="destination",
                            cascade="all, delete-orphan", order_by="Hotspot.id")

class Hotspot(db.Model):
    __tablename__ = "hotspots"
    id, destination_id (FK destinations.id, not null), title (not null),
    description (Text), x_position, y_position, z_position (Float, default 0.0),
    image_path, audio_path
```
Paths are stored relative to `static/` (for example `models/muzium_perang.glb`).

## Design notes
- Fields match the specified schema exactly. Interesting facts are stored inside `description` (paragraph, then a `Facts:` bullet list), avoiding extra columns. `to_dict()` splits them for the API.
- Gallery images for a destination are derived from the hotspot `image_path` values plus `hero_image`, so no gallery table is needed.
- SQLite foreign keys are enabled with a `PRAGMA foreign_keys=ON` connect listener so cascade delete works.
- The database URI defaults to `sqlite:///virtualtourism.db` (instance folder resolved by Flask-SQLAlchemy) and can be overridden by `DATABASE_URL`.

## Seed
`app/seed.py: seed_if_empty()` is called inside the app context after `create_all()`. It checks `Destination.query.count() == 0`, then inserts Muzium Perang Penang and its 10 hotspots from `seed_data.py` (see content spec for text and coordinates). Because it runs only on an empty table, repeated runs create no duplicates.

## Error handling
Commit inside try/except with `db.session.rollback()` on failure; log and re-raise at startup so a broken seed is visible.

## Testing
Create an in-memory DB, run seed twice, assert 1 destination and 10 hotspots; delete the destination and assert 0 hotspots remain.

## As built
- Database file: `instance/virtualtourism.db` (Flask-SQLAlchemy resolves `sqlite:///virtualtourism.db` into the instance folder); override with `DATABASE_URL`.
- Seed: `app/seed_data.py` holds the destination text, 10 hotspots (positions in glTF metres from the Blender export) and asset paths; `app/seed.py: seed_if_empty()` runs inside `create_app`.
- Verified: a fresh database started under gunicorn with two workers (`--preload`) produced exactly 1 destination and 10 hotspots.
- Deleting a destination cascades to its hotspots (`PRAGMA foreign_keys=ON` listener).
