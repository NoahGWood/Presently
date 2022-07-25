import os
import stripe
from flask import Blueprint, flash, render_template, request, url_for, current_app, abort, jsonify
from flask_security import current_user, auth_required
from werkzeug.utils import redirect

payment_pages = Blueprint("payment_pages", __name__, url_prefix='/pay')

stripe_keys = {
    "secret": os.environ["STRIPE_SECRET_KEY"],
    "public": os.environ["STRIPE_PUBLIC_KEY"],
    "endpoint": os.environ["STRIPE_ENDPOINT_SECRET"]
}

stripe.api_key = stripe_keys["secret"]


@payment_pages.route("/", methods=["GET"])
@auth_required()
def pay():
    return render_template("pay.html", user=current_user)


@payment_pages.route("/config")
def get_payment_config():
    stripe_config = {"publicKey": stripe_keys["public"]}
    return jsonify(stripe_config)


@payment_pages.route("/success")
def success():
    return render_template("success.html")


@payment_pages.route("/cancelled")
def cancel():
    return render_template("cancelled.html")


@payment_pages.route("/stripehook",  methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_keys["endpoint"]
        )

    except ValueError as e:
        return "Invalid payload", 400

    except stripe.error.SignatureVerificationError as e:
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":
        print("Payment success")

    return "Success", 200


@payment_pages.route("/create-checkout-session/<credits>")
@auth_required()
def create_checkout_session(credits=0):
    domain_url = "http://127.0.0.1:5000/pay/"
    stripe.api_key = stripe_keys['secret']
    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=current_user.id,
            success_url=domain_url +
            "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "cancelled",
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "name": "credits",
                    "quantity": credits,
                    "currency": "usd",
                    "amount": "100"  # str(int(credits) * 100)
                }
            ]
        )
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403
    # return domain_url
