import os
from flask import Blueprint, flash, render_template, request, url_for, current_app, abort
from flask_security import current_user, auth_required
from werkzeug.utils import redirect

profile_pages = Blueprint("profile_pages", __name__, url_prefix='/profile')

@profile_pages.route("/", methods=["GET"])
@auth_required()
def profile():
    presentations = current_user.presentations
    ps = []
    for p in presentations:
        pres = {}
        pres['title'] = str(p.title)
        pres['file']= str(p.files[0].filepath.split('.')[0])
        ps.append(pres)
    return render_template("profile.html", user=current_user, presentations=ps)