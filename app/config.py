import os
from dotenv import load_dotenv

load_dotenv()


def _list(name):
    return [x.strip().lower() for x in os.environ.get(name, "").split(",") if x.strip()]


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///virtualtourism.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 60 * 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "0") == "1"
    ADMIN_EMAILS = _list("ADMIN_EMAILS")
    # Judge/demo access without OAuth credentials. DEMO_LOGIN gives a normal user.
    # DEMO_ADMIN_KEY (if set) lets /login/demo-admin?key=... sign in as an admin.
    DEMO_LOGIN = os.environ.get("DEMO_LOGIN", "1") == "1"
    DEMO_ADMIN_KEY = os.environ.get("DEMO_ADMIN_KEY", "")
    OAUTH = {
        "google": (os.environ.get("GOOGLE_CLIENT_ID"), os.environ.get("GOOGLE_CLIENT_SECRET")),
        "microsoft": (os.environ.get("MICROSOFT_CLIENT_ID"), os.environ.get("MICROSOFT_CLIENT_SECRET")),
        "github": (os.environ.get("GITHUB_CLIENT_ID"), os.environ.get("GITHUB_CLIENT_SECRET")),
    }
