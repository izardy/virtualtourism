import os
from flask import Blueprint, abort, current_app, render_template, request, url_for
from ..extensions import db
from ..models import Destination

bp = Blueprint("main", __name__)


def gallery_images(dest):
    """Hero + hotspot images + any files in static/images/gallery/<slug>/ (deduplicated, in order)."""
    seen, out = set(), []

    def add(p, caption=""):
        if p and p not in seen:
            seen.add(p)
            out.append({"path": p, "caption": caption})

    add(dest.hero_image, dest.name)
    for h in dest.hotspots:
        add(h.image_path, h.title)
    folder = os.path.join(current_app.root_path, "static", "images", "gallery", dest.slug)
    if os.path.isdir(folder):
        for f in sorted(os.listdir(folder)):
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                add(f"images/gallery/{dest.slug}/{f}", "")
    return out


@bp.route("/favicon.ico")
def favicon():
    from flask import redirect, url_for
    return redirect(url_for("static", filename="favicon.svg"), code=301)


@bp.route("/")
def index():
    destinations = Destination.query.order_by(Destination.id).all()
    featured = destinations[0] if destinations else None
    return render_template("index.html", featured=featured, destinations=destinations)


@bp.route("/explore")
def explore():
    q = (request.args.get("q") or "").strip()
    query = Destination.query
    if q:
        query = query.filter(Destination.name.ilike(f"%{q}%"))
    return render_template("explore.html", destinations=query.order_by(Destination.name).all(), q=q)


@bp.route("/destination/<int:dest_id>")
def destination(dest_id):
    dest = db.session.get(Destination, dest_id) or abort(404)
    return render_template("destination.html", d=dest, gallery=gallery_images(dest), vr_ready=bool(dest.model_path))


@bp.route("/viewer/<int:dest_id>")
def viewer(dest_id):
    dest = db.session.get(Destination, dest_id) or abort(404)
    if not dest.model_path:
        abort(404)
    mode = request.args.get("mode")
    # lighter phone model next to the main one (<name>_mobile.glb: 1k textures, cheaper trees), if it exists
    stem, ext = os.path.splitext(dest.model_path)
    lite = f"{stem}_mobile{ext}"
    model_lite = url_for("static", filename=lite) if os.path.isfile(os.path.join(current_app.root_path, "static", lite)) else ""
    return render_template("viewer.html", d=dest, vr_auto=request.args.get("vr") == "1", mode=mode if mode in ("free", "guided") else "",
                           model_lite=model_lite)
