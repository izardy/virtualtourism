import os
from flask import Blueprint, abort, current_app, jsonify
from ..extensions import db
from ..models import Destination

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/destinations")
def destinations():
    return jsonify([d.to_dict() for d in Destination.query.order_by(Destination.name)])


@bp.route("/destinations/<int:dest_id>/hotspots")
def hotspots(dest_id):
    dest = db.session.get(Destination, dest_id) or abort(404)
    return jsonify({"destination": dest.to_dict(), "hotspots": [h.to_dict() for h in dest.hotspots],
                    "points_url": _points_url(dest)})


def _points_url(dest):
    """Optional JSON listing every labelled spot on the model (static/data/<model name>_points.json)."""
    if not dest.model_path:
        return None
    stem = os.path.splitext(os.path.basename(dest.model_path))[0]
    rel = f"data/{stem}_points.json"
    return f"/static/{rel}" if os.path.isfile(os.path.join(current_app.root_path, "static", rel)) else None
