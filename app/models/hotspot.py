from ..extensions import db


class Hotspot(db.Model):
    __tablename__ = "hotspots"
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)          # paragraph(s), then an optional "Facts:" bullet list
    x_position = db.Column(db.Float, default=0.0)
    y_position = db.Column(db.Float, default=0.0)
    z_position = db.Column(db.Float, default=0.0)
    image_path = db.Column(db.String(300))
    audio_path = db.Column(db.String(300))

    def split_description(self):
        text = self.description or ""
        body, _, facts = text.partition("\nFacts:")
        items = [ln.strip()[1:].strip() for ln in facts.splitlines() if ln.strip().startswith("-")]
        return body.strip(), items

    def to_dict(self):
        body, facts = self.split_description()
        return {"id": self.id, "title": self.title, "description": body, "facts": facts,
                "position": [self.x_position or 0.0, self.y_position or 0.0, self.z_position or 0.0],
                "image": self.image_path, "audio": self.audio_path}
