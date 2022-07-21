import os
import stripe
from flask import Blueprint, flash, render_template, request, url_for, current_app, abort, jsonify
from flask_security import current_user, auth_required
from werkzeug.utils import redirect

payment_pages = Blueprint("payment_pages", __name__, url_prefix='/pay')

stripe_keys = {
    "secret": os.environ["STRIPE_SECRET_KEY"],
    "public": os.environ["STRIPE_PUBLIC_KEY"]
}

stripe.api_key = stripe_keys["secret"]

@payment_pages.route("/", methods=["GET"])
@auth_required()
def pay():
    return render_template("pay.html", name=current_user.email, presentations=current_user.presentations)

@payment_pages.route("/config")
def get_payment_config():
    stripe_config = {"publicKey": stripe_keys["public"]}
    return jsonify(stripe_config)

@payment_pages.route("/callback")
def callback():
    return 