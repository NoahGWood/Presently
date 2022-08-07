"""Special utilities for administrators."""
from database import db_session
from models import *

def GetAllUsers():
    """Returns a list of all users"""
    return db_session.query(User).all()

def GetAllSubscribers():
    """Returns all subscriptions"""
    return db_session.query(SubscriptionUsers).all()

def GetUserById(id):
    """Returns a user by id"""
    return db_session.query(User).filter(User.id==id).first()

def GetSubscriptionById(id):
    """Returns a subscription by the id"""
    return db_session.query(Subscription).filter(Subscription.id==id).first()

