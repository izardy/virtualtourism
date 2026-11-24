from flask import Blueprint, render_template
from flask_login import current_user, login_required

bp = Blueprint("user", __name__)


@bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html", u=current_user)
