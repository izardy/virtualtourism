import re
from ..extensions import db


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "_", (name or "").lower()).strip("_")


class Destination(db.Model):
    __tablename__ = "destinations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    category = db.Column(db.String(100))
    thumbnail = db.Column(db.String(300))     # path relative to static/
    hero_image = db.Column(db.String(300))
    model_path = db.Column(db.String(300))
    hotspots = db.relationship("Hotspot", backref="destination", cascade="all, delete-orphan",
                               order_by="Hotspot.id")

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def paragraphs(self):
        return [p.strip() for p in (self.description or "").split("\n\n") if p.strip()]

    def to_dict(self):
        return {"id": self.id, "name": self.name, "location": self.location, "category": self.category,
                "thumbnail": self.thumbnail, "hero_image": self.hero_image, "model_path": self.model_path}
