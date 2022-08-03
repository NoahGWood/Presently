
import os
from flask import Flask, render_template, render_template_string, url_for, send_from_directory
from flask_security import Security, current_user, auth_required, hash_password, SQLAlchemySessionUserDatastore
from database import db_session, init_db, create_session
from models import User, Role, File, PresentationUser, Presentation
from utils import is_active, create_customer
import datetime

app = Flask(__name__)

# Generate a nice key using secrets.token_urlsafe()
app.config['SECRET_KEY'] = os.environ.get(
    "SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
# Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
# Generate a good salt using: secrets.SystemRandom().getrandbits(128)
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get(
    "SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')

# Allow register users
app.config["SECURITY_REGISTERABLE"] = True
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
# Allow password change
app.config["SECURITY_CHANGEABLE"] = True
# Allow password reset
app.config["SECURITY_RECOVERABLE"] = True
# Track IP Address
app.config["SECURITY_TRACKABLE"] = True

# File upload settings
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS']= ['.txt', 'md', '.docx']

# Security Settings
user_datastore= SQLAlchemySessionUserDatastore(db_session, User, Role)
security= Security(app, user_datastore)


@ app.template_filter('epoch')
def epoch(s):
    t= datetime.datetime.fromtimestamp(int(s))
    t= t.strftime('%B %-d, %Y')
    return t  # datetime.datetime.fromtimestamp(s)

@ app.before_first_request
def create_user():
    init_db()
    if not user_datastore.find_user(email="test@me.com"):
        user_datastore.create_user(
            email="test@me.com", password=hash_password("password"))
    db_session.commit()
    create_file_db()
    db_session.commit()

def create_file_db():
    usr=  User.query.first()
    if not usr.presentations:
        # Create a test presentation
        pres= Presentation(title='Test')
        f = File(ftype='text', filepath='static/uploads/test.txt', presentation_id=pres.id)
        pres.files.append(f)
        usr.presentations.append(pres)
        db_session.add(pres)
        db_session.add(f)
        db_session.add(usr)


@ app.before_request
def _create_session():
    if db_session == None:
        create_session()

@ app.after_request
def remove_session(req):
    db_session.remove()
    return req

# Views
@ app.route("/")
def home():
    if current_user.is_authenticated:
        # Check if we have an account
        if current_user.stripeCustomerId == None:
            print("NO STRIPE USER ID")
            create_customer()
        else:
            print(current_user.stripeCustomerId)
            print(len(current_user.subscription))
    return render_template("index.html")

@ app.route("/about")
def about():
    return render_template("about.html")

@ app.route("/features")
def features():
    return render_template("features.html")

@ app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@ app.route("/dash")
def profile():
    return render_template("dashboard.html")

@ app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@ app.route("/privacy_termly")
def privacy_termly():
    return render_template("privacy_termly.html")

@ app.route("/tos")
def tos():
    return render_template("tos.html")

@ app.route("/tos_termly")
def tos_termly():
    return render_template("tos_termly.html")

@ app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/imgs'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Blueprints
from views.editor import editor_pages
from views.pay import payment_pages

app.register_blueprint(editor_pages)
app.register_blueprint(payment_pages)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
