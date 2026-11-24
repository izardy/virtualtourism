from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from ..extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    username = db.Column(db.String(120), nullable=False)
    avatar_url = db.Column(db.String(500))
    provider = db.Column(db.String(20), nullable=False)       # google | microsoft | github | demo
    provider_id = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("provider", "provider_id", name="uq_provider_user"),)

    @property
    def is_admin(self):
        if self.provider == "demo-admin":
            return bool(current_app.config.get("DEMO_ADMIN_KEY"))
        return bool(self.email) and self.email.lower() in current_app.config["ADMIN_EMAILS"]

    @property
    def initial(self):
        return (self.username or "?")[:1].upper()
