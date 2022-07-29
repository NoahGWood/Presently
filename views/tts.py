import os
from flask import Blueprint, flash, render_template, request, url_for, current_app, abort
from flask_security import current_user, auth_required
from werkzeug.utils import redirect

profile_pages = Blueprint("speech", __name__, url_prefix='/speech')

@profile_pages.route("/<presentation>/<slide>", methods=["GET"])
@auth_required()
def speech_file(presentation, slide):
    pass

@profile_pages.route("/", methods=["GET"])
@auth_required()
def speech():
    return render_template("test.html", name=current_user.email, presentations=current_user.presentations)