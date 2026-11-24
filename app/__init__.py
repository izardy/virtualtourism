import os
import secrets
from flask import Flask, render_template, session
from sqlalchemy import event
from sqlalchemy.engine import Engine
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config
from .extensions import db, login_manager, oauth


@event.listens_for(Engine, "connect")
def _sqlite_fk(dbapi_conn, _):
    if dbapi_conn.__class__.__module__.startswith("sqlite3"):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.update(config)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.index"
    oauth.init_app(app)

    from .auth_providers import register_providers
    register_providers(app)

    from .routes import main, auth, user, admin, api
    for bp in (main.bp, auth.bp, user.bp, admin.bp, api.bp):
        app.register_blueprint(bp)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return db.session.get(User, int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import flash, redirect, url_for
        flash("Please sign in to continue.", "info")
        return redirect(url_for("main.index"))

    @app.context_processor
    def inject_globals():
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_urlsafe(24)
        return {"csrf_token": session["_csrf"], "providers": app.config["ENABLED_PROVIDERS"],
                "demo_login": app.config["DEMO_LOGIN"]}

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(_):
        return render_template("404.html", forbidden=True), 403

    @app.after_request
    def cache_headers(resp):
        # long cache for heavy static assets (models, vendor libs); names change when files change
        from flask import request
        if request.path.startswith("/static/models/") or "/vendor/" in request.path:
            resp.headers.setdefault("Cache-Control", "public, max-age=86400")
        return resp

    with app.app_context():
        os.makedirs(app.instance_path, exist_ok=True)
        db.create_all()
        from .seed import seed_if_empty
        seed_if_empty()
    return app
