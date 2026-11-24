import secrets
from functools import wraps
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Destination, Hotspot
from ..services.uploads import UploadError, delete_upload, save_upload

bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*a, **kw):
        if not current_user.is_admin:
            abort(403)
        return fn(*a, **kw)
    return wrapper


@bp.before_request
def check_csrf():
    if request.method == "POST":
        sent = request.form.get("_csrf", "")
        if not sent or not secrets.compare_digest(sent, session.get("_csrf", "")):
            abort(400, "Invalid form token. Reload the page and try again.")


def _redirect(dest_id=None):
    return redirect(url_for("admin.dashboard", dest=dest_id) if dest_id else url_for("admin.dashboard"))


def _text(name, limit=5000):
    return (request.form.get(name) or "").strip()[:limit]


def _float(name):
    raw = (request.form.get(name) or "0").strip() or "0"
    try:
        return float(raw)
    except ValueError:
        raise UploadError(f"{name.replace('_', ' ')} must be a number")


@bp.route("/")
@admin_required
def dashboard():
    destinations = Destination.query.order_by(Destination.name).all()
    selected = db.session.get(Destination, request.args.get("dest", type=int) or 0) or (destinations[0] if destinations else None)
    return render_template("admin.html", destinations=destinations, selected=selected)


def _apply_destination(d):
    name = _text("name", 200)
    if not name:
        raise UploadError("Name is required")
    d.name, d.location = name, _text("location", 200)
    d.category, d.description = _text("category", 100), _text("description", 20000)
    for field, kind in (("thumbnail", "image"), ("hero_image", "image"), ("model_path", "model")):
        new = save_upload(request.files.get(field), kind)
        if new:
            old = getattr(d, field)
            setattr(d, field, new)
            if old and old != new:
                db.session.flush()
                delete_upload(old)


@bp.route("/destinations", methods=["POST"])
@admin_required
def create_destination():
    d = Destination()
    try:
        _apply_destination(d)
    except UploadError as e:
        flash(str(e), "error")
        return _redirect()
    db.session.add(d)
    db.session.commit()
    flash(f"Added {d.name}.", "success")
    return _redirect(d.id)


@bp.route("/destinations/<int:dest_id>", methods=["POST"])
@admin_required
def update_destination(dest_id):
    d = db.session.get(Destination, dest_id) or abort(404)
    try:
        _apply_destination(d)
    except UploadError as e:
        db.session.rollback()
        flash(str(e), "error")
        return _redirect(dest_id)
    db.session.commit()
    flash("Destination saved.", "success")
    return _redirect(dest_id)


@bp.route("/destinations/<int:dest_id>/delete", methods=["POST"])
@admin_required
def delete_destination(dest_id):
    d = db.session.get(Destination, dest_id) or abort(404)
    files = [d.thumbnail, d.hero_image, d.model_path] + [x for h in d.hotspots for x in (h.image_path, h.audio_path)]
    db.session.delete(d)
    db.session.commit()
    for f in files:
        delete_upload(f)
    flash("Destination deleted.", "success")
    return _redirect()


def _apply_hotspot(h):
    title = _text("title", 200)
    if not title:
        raise UploadError("Title is required")
    h.title, h.description = title, _text("description", 20000)
    h.x_position, h.y_position, h.z_position = _float("x_position"), _float("y_position"), _float("z_position")
    for field, kind in (("image_path", "image"), ("audio_path", "audio")):
        new = save_upload(request.files.get(field.replace("_path", "")), kind)
        if new:
            old = getattr(h, field)
            setattr(h, field, new)
            if old and old != new:
                db.session.flush()
                delete_upload(old)


@bp.route("/destinations/<int:dest_id>/hotspots", methods=["POST"])
@admin_required
def create_hotspot(dest_id):
    db.session.get(Destination, dest_id) or abort(404)
    h = Hotspot(destination_id=dest_id)
    try:
        _apply_hotspot(h)
    except UploadError as e:
        flash(str(e), "error")
        return _redirect(dest_id)
    db.session.add(h)
    db.session.commit()
    flash(f"Hotspot '{h.title}' created.", "success")
    return _redirect(dest_id)


@bp.route("/hotspots/<int:hid>", methods=["POST"])
@admin_required
def update_hotspot(hid):
    h = db.session.get(Hotspot, hid) or abort(404)
    try:
        _apply_hotspot(h)
    except UploadError as e:
        db.session.rollback()
        flash(str(e), "error")
        return _redirect(h.destination_id)
    db.session.commit()
    flash("Hotspot saved.", "success")
    return _redirect(h.destination_id)


@bp.route("/hotspots/<int:hid>/delete", methods=["POST"])
@admin_required
def delete_hotspot(hid):
    h = db.session.get(Hotspot, hid) or abort(404)
    dest_id, files = h.destination_id, [h.image_path, h.audio_path]
    db.session.delete(h)
    db.session.commit()
    for f in files:
        delete_upload(f)
    flash("Hotspot deleted.", "success")
    return _redirect(dest_id)
