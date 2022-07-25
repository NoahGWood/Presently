import os
from flask import Blueprint, flash, render_template, request, url_for, current_app, abort
from flask_security import current_user, auth_required
from werkzeug.utils import redirect
from models import User, File, Presentation, PresentationUser
from database import db_session
import datetime
import hashlib
import uuid

editor_pages = Blueprint("editor_pages", __name__, url_prefix='/editor')


@editor_pages.route("/<presentation>", methods=["GET", "POST"])
@auth_required()
def edit(presentation):
    #    presentation=presentation.split('?')[0]
    a = db_session.query(File).filter(
        File.filepath.contains(presentation+'.txt')
    ).first()
    pres_user = db_session.query(PresentationUser).filter(
        PresentationUser.presentation_id == a.presentation_id
    ).first()
    pres = db_session.query(Presentation).filter(
        Presentation.id == a.presentation_id
    ).first()
    if current_user.id == pres_user.user_id:
        if request.method == "POST":
            txt = request.form['text']
            # Make sure text is not null
            if len(txt) > 0:
                write_text_file(presentation, txt)
            # Redirect back to presentation
            return redirect("/editor/{}".format(presentation))
        else:
            videos = GetVideos(pres)
            text = GetText(a.filepath)
            return render_template("editor.html", name=current_user.email, current=pres, videos=videos, text=text, fname=presentation)
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


def NewPresentation(title, language, translate, genimages, text):
    fname = str(uuid.uuid4())
    write_text_file(fname, text)
    time = datetime.datetime.now()
    p = Presentation(title=title, ctime=time, mtime=time,
                     translate=translate, genimages=genimages)
    f = File(language=language, ctime=time, mtime=time,
             filepath=os.getcwd() + "/static/uploads/{}.txt".format(fname))
    p.files.append(f)
    curr_usr = db_session.query(User).filter(
        User.id == current_user.id).first()
    curr_usr.presentations.append(p)
    db_session.add(p)
    db_session.add(f)
    db_session.add(curr_usr)
    db_session.commit()
    return fname


def write_text_file(fname, text):
    """ Writes text to file fname"""
    # Save text to file
    print("WRITING TEXT")
    print(fname, text)
    with open('static/uploads/{}.txt'.format(fname), 'w') as f:
        f.writelines(text)


def GetText(filepath):
    """Returns the text of file"""
    txt = ''
    with open(filepath, 'r') as f:
        for line in f.readlines():
            txt += line
    return txt


def GetVideos(presentation):
    vids = []
    for f in presentation.files:
        if f.ftype == 'video':
            vids.append(f)
    return vids

@editor_pages.route("/video/<video_id>", methods=["GET"])
@auth_required()
def stream_video(video_id):
    return video_id
    current_user