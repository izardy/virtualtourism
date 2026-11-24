import secrets
from urllib.parse import urlparse
from flask import Blueprint, abort, current_app, flash, redirect, request, session, url_for
from flask_login import login_user, logout_user
from authlib.integrations.base_client.errors import OAuthError

from ..extensions import db, oauth
from ..models import User
from ..auth_providers import normalize_profile

bp = Blueprint("auth", __name__)


def _safe_next(target):
    if not target:
        return None
    p = urlparse(target)
    return target if not p.netloc and not p.scheme and target.startswith("/") and not target.startswith("//") else None


def upsert_user(provider, prof):
    user = User.query.filter_by(provider=provider, provider_id=prof["provider_id"]).first()
    if user is None:
        user = User(provider=provider, provider_id=prof["provider_id"])
        db.session.add(user)
    user.email = prof.get("email") or user.email
    user.username = prof.get("username") or user.username or "Traveller"
    user.avatar_url = prof.get("avatar_url") or user.avatar_url
    db.session.commit()
    return user


@bp.route("/login/<provider>")
def login(provider):
    if provider not in current_app.config["ENABLED_PROVIDERS"]:
        abort(404)
    session["next"] = _safe_next(request.args.get("next")) or ""
    return getattr(oauth, provider).authorize_redirect(url_for("auth.callback", provider=provider, _external=True))


@bp.route("/auth/<provider>/callback")
def callback(provider):
    if provider not in current_app.config["ENABLED_PROVIDERS"]:
        abort(404)
    try:
        kwargs = {"claims_options": {"iss": {"essential": False}}} if provider == "microsoft" else {}
        token = getattr(oauth, provider).authorize_access_token(**kwargs)
        user = upsert_user(provider, normalize_profile(provider, token))
    except (OAuthError, Exception) as exc:   # network errors, denied consent, bad state
        current_app.logger.warning("OAuth login failed for %s: %s", provider, type(exc).__name__)
        flash("Sign-in failed or was cancelled. Please try again.", "error")
        return redirect(url_for("main.index"))
    login_user(user)
    return redirect(_safe_next(session.pop("next", "")) or url_for("user.profile"))


@bp.route("/login-demo")
def login_demo():
    """Sign in as a demo visitor (no OAuth needed). Enabled with DEMO_LOGIN=1."""
    if not current_app.config["DEMO_LOGIN"]:
        abort(404)
    user = upsert_user("demo", {"provider_id": "visitor-" + secrets.token_hex(3), "username": "Demo Traveller",
                                "email": None, "avatar_url": None})
    login_user(user)
    flash("Signed in as a demo visitor.", "info")
    return redirect(_safe_next(request.args.get("next")) or url_for("user.profile"))


@bp.route("/login-demo-admin")
def login_demo_admin():
    """Judge access to the admin panel: /login-demo-admin?key=<DEMO_ADMIN_KEY>."""
    key = current_app.config["DEMO_ADMIN_KEY"]
    if not key or not secrets.compare_digest(request.args.get("key", ""), key):
        abort(404)
    user = upsert_user("demo-admin", {"provider_id": "judge", "username": "Demo Admin", "email": None, "avatar_url": None})
    login_user(user)
    return redirect(url_for("admin.dashboard"))


@bp.route("/logout")
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))
