import os
from flask import Blueprint, flash, render_template, request, url_for, current_app, abort
from flask_security import current_user, auth_required
from werkzeug.utils import redirect

profile_pages = Blueprint("profile_pages", __name__, url_prefix='/profile')

@profile_pages.route("/", methods=["GET"])
@auth_required()
def dump():
    return render_template("test.html", name=current_user.email, presentations=current_user.presentations)