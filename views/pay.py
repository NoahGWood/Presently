"""Views and logic for stripe payment integration"""
import os
import stripe
from flask import Blueprint, render_template, request, jsonify
from flask_security import current_user, auth_required
from werkzeug.utils import redirect
from utils import stripe_keys, set_stripe_user, set_subscription

payment_pages = Blueprint("payment_pages", __name__, url_prefix='/pay')


@payment_pages.route("/", methods=["GET"])
@auth_required()
def pay():
    """Main /pay view"""
    return render_template("pay.html", user=current_user)


@payment_pages.route("/config")
def get_payment_config():
    """Returns the configuration info"""
    stripe_config = {"publicKey": stripe_keys["public"]}
    return jsonify(stripe_config)


@payment_pages.route("/success/<session>")
def success(session):
    """Landing page after subscribe"""
    return render_template("success.html")


@payment_pages.route("/onboarding/<session>", methods=['GET', 'SET'])
def onboarding(session):
    """Landing page after subscribe"""
    return render_template('onboarding.html')


@payment_pages.route("/cancelled")
def cancel():
    """Landing page after canceled session."""
    return render_template("cancelled.html")

# @require_POST
# @csrf_exempt

@payment_pages.route("/stripe_webhook", methods=['POST'])
def Webhook():
    """Stripe webhook.

    Implements: subscriptions
    """
    print("STARTING WEBHOOK!")
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ["STRIPE_ENDPOINT_SECRET"]
        )
    except ValueError as e:
        # Invalid payload
        return jsonify(status=400)
#        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify(status=400)

    # Handle event
    if event.type in ('customer.subscription.created', 'customer.subscription.updated', 'customer.subscription.deleted'):
        set_subscription(event)

    print('Handled event type {}'.format(event['type']))

    return jsonify(success=True)


@payment_pages.route("/create-checkout-session/", methods=["POST"])
@auth_required()
def create_checkout_session():
    """Creates a new checkout session."""
    domain_url = os.environ.get("DOMAIN_URL", "http://127.0.0.1:5000/pay/")
    stripe.api_key = stripe_keys['secret']
    try:
        if len(current_user.subscription) == 0:
            checkout_session = stripe.checkout.Session.create(
                customer=current_user.stripeCustomerId,
                success_url=domain_url +
                "success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "cancelled",
                payment_method_types=["card"],
                mode="subscription",
                line_items=[
                    {
                        "price": "price_1LSHpwFQdRpLHHqXOcg9WTfo",
                        "quantity": "1"
                    }
                ]
            )
        else:
            print(current_user.stripeCustomerId)
            try:
                checkout_session = stripe.billing_portal.Session.create(
                    customer=current_user.stripeCustomerId,
                    return_url=domain_url,
                )
            except Exception as e:
                new_customer = stripe.Customer.create(
                    email=current_user.email
                )
                set_stripe_user(current_user, new_customer.id)
                checkout_session = stripe.checkout.Session.create(
                    customer=new_customer.id,
                    success_url=domain_url +
                    "success?session_id={CHECKOUT_SESSION_ID}",
                    cancel_url=domain_url + "cancelled",
                    payment_method_types=["card"],
                    mode="subscription",
                    line_items=[
                        {
                            "price": "price_1LSHpwFQdRpLHHqXOcg9WTfo",
                            "quantity": "1"
                        }
                    ]
                )
        # jsonify({"sessionId": checkout_session["id"]})
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 403
