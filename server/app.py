
import os
from flask import Flask, render_template, render_template_string, url_for
from flask_security import Security, current_user, auth_required, hash_password, SQLAlchemySessionUserDatastore
from database import db_session, init_db, create_session
from models import User, Role, File, PresentationUser, Presentation 
#from dotenv import load_dotenv
#load_dotenv()
#application_key_id = os.environ.get("AppKeyID")

app = Flask(__name__)

# Generate a nice key using secrets.token_urlsafe()
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
# Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
# Generate a good salt using: secrets.SystemRandom().getrandbits(128)
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')

# Allow register users
app.config["SECURITY_REGISTERABLE"] = True
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False

# File upload settings
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 *1024
app.config['UPLOAD_EXTENSIONS'] = ['.txt', 'md', '.docx']

# Security Settings
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
security = Security(app, user_datastore)


@app.before_first_request
def create_user():
    init_db()
    if not user_datastore.find_user(email="test@me.com"):
        user_datastore.create_user(email="test@me.com", password=hash_password("password"))
    db_session.commit()
    create_file_db()
    db_session.commit()    

def create_file_db():
    usr =  User.query.first()
    if not usr.presentations:
        # Create a test presentation
        pres = Presentation(title='Test')
        f = File(ftype='text',filepath='static/uploads/test.txt', presentation_id=pres.id)
        pres.files.append(f)
        usr.presentations.append(pres)
        db_session.add(pres)
        db_session.add(f)
        db_session.add(usr)


@app.before_request
def _create_session():
    if db_session == None:
        create_session()

@app.after_request
def remove_session(req):
    db_session.remove()
    return req

# Views
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/features")
def features():
    return render_template("features.html")

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route("/dash")
def profile():
    return render_template("dashboard.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/privacy_termly")
def privacy_termly():
    return render_template("privacy_termly.html")

@app.route("/tos")
def tos():
    return render_template("tos.html")

@app.route("/tos_termly")
def tos_termly():
    return render_template("tos_termly.html")

#@app.route("/dashboard")
#@auth_required()
#def dashboard():
#    return render_template_string('Hello {{email}} !', email=current_user.email)

# Blueprints
from views.test import profile_pages
from views.editor import editor_pages
from views.pay import payment_pages

app.register_blueprint(profile_pages)
app.register_blueprint(editor_pages)
app.register_blueprint(payment_pages)

#from views.upload import upload_pages
#from views.features import features_pages

#app.register_blueprint(upload_pages)
#app.register_blueprint(features_pages)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
