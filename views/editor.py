import os
from flask import Blueprint, flash, render_template, request, url_for, current_app, abort
from flask_security import current_user, auth_required
from werkzeug.utils import redirect
from database import db_session
from utils import *

editor_pages = Blueprint("editor_pages", __name__, url_prefix='/editor')

@editor_pages.route("/<presentation>", methods=["GET", "POST"])
@auth_required()
def edit(presentation):
    access, pres, pres_file = AuthPresentation(current_user, presentation)
    if access:
        if request.method == "POST":
            txt = request.form['text']
            # Make sure text is not null
            if len(txt) > 0:
                print("YES!")
                write_text_file(presentation, txt)
            # Redirect back to presentation
            return redirect("/editor/{}".format(presentation))
        else:
            videos = GetVideos(pres)
            print(pres_file.filepath)
            text = GetText(pres_file.filepath)
            return render_template("editor.html", name=current_user.email, current=pres, videos=videos, text=text.replace("\n","\\n").replace("\r","\\r"), fname=presentation)
    else:
        return redirect("/editor/new")


@editor_pages.route("/new", methods=["GET", "POST"])
@auth_required()
def new():
    if request.method == "POST":
        title = request.form['title']
        lang = request.form['languages']
        if 'translate' in request.form:
            translate = True
        else:
            translate = False
        if 'gen-image' in request.form:
            genimages = True
        else:
            genimages = False
        text = request.form['text']
        if len(text) <= 1:
            return render_template("new.html")
        else:
            fname = NewPresentation(title, lang, translate, genimages, text)
            return redirect("/editor/{}".format(fname))
    return render_template("new.html", name=current_user.email, presentations=current_user.presentations)


@editor_pages.route("/submitted")
@auth_required()
def submitted():
    return render_template("submitted.html")

@editor_pages.route("/video/<video_id>", methods=["GET"])
@auth_required()
def stream_video(video_id):
    return video_id
    current_user