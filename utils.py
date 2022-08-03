import uuid
import datetime
import stripe
import os
from database import db_session
from models import *
from file_manager import load_file_text, upload_file_from_txt
from functools import wraps
from flask import redirect, url_for
from flask_security import current_user, SQLAlchemySessionUserDatastore, hash_password
from twilio.rest import Client

stripe_keys = {
    "secret": os.environ["STRIPE_SECRET_KEY"],
    "public": os.environ["STRIPE_PUBLIC_KEY"],
    "endpoint": os.environ["STRIPE_ENDPOINT_SECRET"]
}

stripe.api_key = stripe_keys["secret"]


# Security Settings
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)


def TextAccountInfo(phone, email, password):
    client = Client(os.environ['TWILIO_ACCOUNT_SID'],
                    os.environ['TWILIO_AUTH_TOKEN'])
    message = client.messages.create(
        body="""
Thanks for subscribing to presently!
Here are your login credentials:
email: {}
password: {}""".format(email, password),
        from_=str(os.environ['TWILIO_PHONE_NUMBER']),
        to=str(phone)
    )


def FindPresentationFile(presentation):
    return db_session.query(File).filter(
        File.filepath.contains(presentation+'.txt')
    ).first()


def FindAllPresentationAudio(presentation):
    audios = []
    for pf in presentation.files:
        if 'audio' in pf.filetype:
            audios.append(pf)
    return audios


def FindAudioBySlide(audio_list, slide):
    """Returns the file for an approriate slide."""
    for each in audio_list:
        if 'audio{}'.format(slide) in each.filetype:
            return each
    return None


def FindPresentationOwnerByFile(pfile):
    return db_session.query(PresentationUser).filter(
        PresentationUser.presentation_id == pfile.presentation_id
    ).first()


def GetPresentationByFile(pfile):
    return db_session.query(Presentation).filter(
        Presentation.id == pfile.presentation_id
    ).first()


def UserCanAccessPresentation(user, pres_user):
    """Returns true if user can access presentation, false if not."""
    return user.id == pres_user.user_id


def AuthPresentation(user, presentation):
    """Handles authenticating user to presentation.

        Returns tuple (true, presentation, main file) if available
    """
    pres_file = FindPresentationFile(presentation)
    pres_user = FindPresentationOwnerByFile(pres_file)
    pres = GetPresentationByFile(pres_file)
    return UserCanAccessPresentation(user, pres_user), pres, pres_file


def NewPresentation(current_user, title, language, translate, genimages, text):
    fname = str(uuid.uuid4())
    write_text_file(fname, text)
    time = datetime.datetime.now()
    p = Presentation(title=title, ctime=time, mtime=time,
                     translate=translate, genimages=genimages)
    f = File(language=language, ctime=time, mtime=time,
             filepath="{}.txt".format(fname))
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
    upload_file_from_txt(fname+'.txt', text)


def GetText(filepath):
    """Returns the text of file"""
    txt = ''
    return load_file_text(filepath)


def GetVideos(presentation):
    vids = []
    for f in presentation.files:
        if f.ftype == 'video':
            vids.append(f)
    return vids


def is_active(current_user):
    """Returns true or false depending on whether a user has an active subscription."""
    subscription = subscription_info(current_user)
    if subscription != None:
        if subscription['status'] == 'active' or subscription['status'] == 'trialing':
            return True
    return False


def subscription_info(current_user):
    """Returns the subscription information of a current user."""
    if current_user.stripeSubscriptionId != None:
        return stripe.Subscription.retrieve(current_user.stripeSubscriptionId)
    else:
        return None


def set_stripe_user(current_user, stripeCustomerId):
    if current_user.stripeCustomerId == None:
        current_user.stripeCustomerId = stripeCustomerId
    else:
        # Weird, log for now; heroku logs print stmts
        print("SETTING NEW STRIPE USER: ", current_user.id)
        print("OLD: ", current_user.stripeCustomerId, " NEW: ", stripeCustomerId)
        current_user.stripeCustomerId = stripeCustomerId
    db_session.commit()


def set_invoice(event):
    pass


def set_customer(event):
    # Check if contains session info
    # Otherwise try to link by email
    print(event)


def create_customer(email, phone, stripeCustomerId):
    """Creates and returns a customer."""
    password = "password"
    user_datastore.create_user(
        email=email, password=hash_password(password),
        tf_phone_number=str(phone), stripeCustomerId=stripeCustomerId)
    db_session.commit()
    TextAccountInfo(phone, email, password)
    return db_session.query(User).filter(User.email == email).first()


def set_subscription(event):
    # Check if subscription exists
    subscription = db_session.query(Subscription).filter(
        Subscription.stripeSubscriptionId == event.data.object.id
    ).first()
    # Get the customer
    customer = db_session.query(User).filter(
        User.stripeCustomerId == event.data.object.customer
    ).first()
    if subscription != None:
        # Update subscription
        subscription.stripeCustomerId = event.data.object.customer
        subscription.stripeSubscriptionId = event.data.object.id
        subscription.status = event.data.object.status
        subscription.starts = str(event.data.object.current_period_start)
        subscription.ends = str(event.data.object.current_period_end)
        latest_invoice = event.data.object.latest_invoice
    else:
        # Create subscription
        subscription = Subscription(
            stripeSubscriptionId=str(event.data.object.id),
            status=str(event.data.object.status),
            starts=str(event.data.object.current_period_start),
            ends=str(event.data.object.current_period_end),
            latest_invoice=str(event.data.object.latest_invoice),
        )
    if customer != None:
        subscription.user_id = int(customer.id)
        subscription.stripeCustomerId = str(customer.stripeCustomerId)
    else:
        # We have a new customer without a linked account
        # Check first if we have a current user
        if current_user.is_authenticated:
            # We have a user account to link
            subscription.user_id = current_user.id
        else:
            # Get customer object from stripe
            sc = stripe.Customer.retrieve(event.data.object.customer)
            if sc and sc.email:
                # Make sure we don't have an existing account
                customer = db_session.query(User).filter(
                    User.email == sc.email
                ).first()
                if customer == None:
                    customer = create_customer(
                        sc.email,
                        sc.phone,
                        sc.id)
                subscription.user_id = int(customer.id)
                subscription.stripeCustomerId = str(customer.stripeCustomerId)
            else:
                return
    customer.subscription = [subscription]
    db_session.add(subscription)
    db_session.add(customer)
    db_session.commit()


def user_subscribed(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        S = db_session.query(Subscription).filter(
            Subscription.stripeCustomerId == current_user.stripeCustomerId
        ).first()
        if S != None and S.status in ('trialing', 'active'):
            # print(current_user.subscription.status)
            #    if current_user.subscription.status in ('trialing', 'active'):
            return f(*args, **kwargs)
        else:
            return redirect(url_for("payment_pages.pay"))
    return decorator
