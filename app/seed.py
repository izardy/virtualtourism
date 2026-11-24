from .extensions import db
from .models import Destination, Hotspot
from .seed_data import DESTINATION, HOTSPOTS


def seed_if_empty():
    """Insert the MVP destination once. Safe to call on every start."""
    if Destination.query.count() > 0:
        return
    dest = Destination(**DESTINATION)
    db.session.add(dest)
    db.session.flush()
    for h in HOTSPOTS:
        db.session.add(Hotspot(destination_id=dest.id, **h))
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
