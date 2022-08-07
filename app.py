""" The main application file
"""
import os
import datetime
from flask import Flask, render_template, send_from_directory, redirect
from flask_principal import Principal
from flask_security import Security, current_user, hash_password
from flask_security import SQLAlchemySessionUserDatastore, user_registered
from database import db_session, init_db, create_session
from models import User, Role, RolesUsers
from views.pay import payment_pages
from views.editor import editor_pages
from views.admin import admin_pages
from utils import create_customer_id

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
# Disable mail for now
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
app.config["SECURITY_SEND_PASSWORD_CHANGE_EMAIL"] = False
# Allow password change
app.config["SECURITY_CHANGEABLE"] = True
# Allow password reset
app.config["SECURITY_RECOVERABLE"] = True
# Track IP Address
app.config["SECURITY_TRACKABLE"] = True

# File upload settings
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.txt', 'md', '.docx']

# Security Settings
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
security = Security(app, user_datastore)

# Load principal
principals = Principal(app)

# Set up some filters

@app.template_filter('epoch')
def epoch(s):
	if type(s) == type(""):
		t = datetime.datetime.fromtimestamp(int(s))
	else:
		t = s
	t = t.strftime('%B %-d, %Y')
	return t  # datetime.datetime.fromtimestamp(s)

@app.template_filter('len')
def template_len(s):
    return len(s)

# Set up database if not already exist

@app.before_first_request
def create_user():
    """Used to create initial admin user."""
    init_db()
    # Create admin & user roles if not exist
    if not db_session.query(Role).filter(Role.name=='admin').first():
        admin_role = Role(
            name="admin",
            description="Site administration"
        )
        db_session.add(admin_role)
        db_session.commit()
    else:
        admin_role = db_session.query(Role).filter(Role.name=='admin').first()
    if not db_session.query(Role).filter(Role.name=='user').first():
        user_role = Role(
            name="user",
            description="Default site user"
        )
        db_session.add(user_role)
        db_session.commit()
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "test@me.com")
    ADMIN_PASS = os.environ.get("ADMIN_PASSWORD", 'password')
    if not user_datastore.find_user(email=ADMIN_EMAIL):
        user_datastore.create_user(
            email=ADMIN_EMAIL,
            password=ADMIN_PASS,
            roles=[admin_role, user_role]
        )
        db_session.commit()
    # Create a test accont if not exist
    if not user_datastore.find_user(email="test@me.com"):
        user_datastore.create_user(
            email="test@me.com",
            password="password",
            roles=[user_role]
        )
        db_session.commit()


# Set default role for new users
@user_registered.connect_via(app)
def user_registered_sighandler(app, user, confirm_token):
    default_role = user_datastore.find_role("user")
    user_datastore.add_role_to_user(user, default_role)
    db.session.commit()

@app.before_request
def _create_session():
    """Used to create a new db_session for each connection."""
    if db_session is None:
        create_session()


@app.after_request
def remove_session(req):
    """Removes db_session after each connection."""
    db_session.remove()
    return req

# Handle 403 forbidden
@app.errorhandler(403)
def page_not_found(e):
    return redirect('/')

# Views
@app.route("/")
def home():
    """Home page"""
    if current_user.is_authenticated:
        # Check if we have an account
        if current_user.stripeCustomerId is None:
            print("NO STRIPE USER ID")
            create_customer_id()
            #create_customer()
        else:
            print(current_user.stripeCustomerId)
            print(len(current_user.subscription))
    return render_template("index.html")


@app.route("/about")
def about():
    """About Page"""
    return render_template("about.html")


@app.route("/features")
def features():
    """Features Page"""
    return render_template("features.html")


@app.route("/pricing")
def pricing():
    """Pricing Page"""
    return render_template("pricing.html")


@app.route("/privacy")
def privacy():
    """Privacy Page"""
    return render_template("privacy.html")


@app.route("/privacy_termly")
def privacy_termly():
    """Privacy loader (used to sideload termly page)"""
    return render_template("privacy_termly.html")


@app.route("/tos")
def tos():
    """Terms of Service Page"""
    return render_template("tos.html")


@app.route("/tos_termly")
def tos_termly():
    """TOS loader (used to sideload termly TOS page)"""
    return render_template("tos_termly.html")


@app.route("/favicon.ico")
def favicon():
    """Used to display icon since some browser demand it."""
    return send_from_directory(os.path.join(app.root_path,
                                            'static/imgs'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')

@app.route("/deleted")
def deleted():
    return render_template("deleted.html")

# Blueprints

app.register_blueprint(editor_pages)
app.register_blueprint(payment_pages)
app.register_blueprint(admin_pages)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
