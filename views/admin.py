from flask import Blueprint, render_template, request, jsonify
from flask_security import current_user, auth_required
from werkzeug.utils import redirect
from utils import admin_permission
from admin_utils import GetAllUsers, GetUserById, GetSubscriptionById
from utils import GetText, GetVideos, NewPresentation, user_subscribed, AuthPresentation, write_text_file
admin_pages = Blueprint("admin_pages", __name__, url_prefix='/admin')


@admin_pages.route("/", methods=["GET"])
@auth_required()
@admin_permission.require(http_exception=403)
def admin():
    """Main admin view"""
    return render_template("admin.html", users=GetAllUsers())

@admin_pages.route("/edit/<accountId>")
@auth_required()
@admin_permission.require(http_exception=403)
def edit_account(accountId):
    return render_template("admin/editor.html", user=GetUserById(int(accountId)))

@admin_pages.route("/edit/subscription/edit/<subscriptionId>")
@auth_required()
@admin_permission.require(http_exception=403)
def edit_subscription(subscriptionId):
    return render_template('admin/subscription_editor.html', subscription=GetSubscriptionById(subscriptionId))

# Might need to moderate content at some point, let's have an
# admin editor for the user presentations
@admin_pages.route("/edit/<accountId>/<presentation>", methods=["GET", "POST"])
@auth_required()
@admin_permission.require(http_exception=403)
def edit_presentation(accountId, presentation):
    """Presentation editor view"""
    user = GetUserById(accountId)
    access, pres, pres_file = AuthPresentation(user, presentation)
    if request.method == "POST":
        txt = request.form['text']
        # Make sure text is not null
        if len(txt) > 0:
            print("YES!")
            write_text_file(presentation, txt)
        # Redirect back to presentation
        return redirect("/admin/edit/{}/{}".format(accountId, presentation))
    else:
        videos = GetVideos(pres)
        print(pres_file.filepath)
        text = GetText(pres_file.filepath)
        return render_template("editor.html", name=user.email, current=pres,
                               videos=videos,
                               text=text.replace(
                                   "\n", "\\n").replace("\r", "\\r"), fname=presentation)

@admin_pages.route("/edit/delete/<accountId>/<presentation>")
@auth_required()
@admin_permission.require(http_exception=403)
def delete_presentation(accountId, presentation):
    pass

@admin_pages.route("/new/presentation/<userId>", methods=["GET", "POST"])
@auth_required()
@admin_permission.require(http_exception=403)
def new(userId):
    user = GetUserById(userId)
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
            fname = NewPresentation(
                user, title, lang, translate, genimages, text)
            return redirect("/admin/edit/{}/{}".format(userId, fname))
    return render_template("new.html", name=user.email,
                           presentations=user.presentations)
