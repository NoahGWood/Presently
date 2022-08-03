from database import Base
from flask_security import UserMixin, RoleMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, \
    String, ForeignKey


class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))


class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

class Invoice(Base):
    __tablename__ = 'invoice'
    id = Column(Integer, primary_key=True)
    customerId = Column(String(255))
    url = Column(String(255), unique=True)
    pdf = Column(String(255), unique=True)
 
class InvoiceUsers(Base):
    __tablename__ = 'invoice_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(),  ForeignKey('user.id'))
    invoice_id = Column('invoice_id', Integer(), ForeignKey('invoice.id'))

class SubscriptionUsers(Base):
    __tablename__ = 'subscription_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(),  ForeignKey('user.id'))
    subscription_id = Column('subscription_id', Integer(), ForeignKey('subscription.id'))

class Subscription(Base):
    __tablename__ = 'subscription'
    id = Column(Integer, primary_key=True)
    stripeCustomerId = Column(String(255), nullable=False)
    stripeSubscriptionId = Column(String(255), nullable=False)
    status = Column(String(30), nullable=False)
    starts = Column(String(20))
    ends = Column(String(20))
    latest_invoice = Column(String(255))
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))


class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(255), unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    confirmed_at = Column(DateTime())
    tf_phone_number = Column(String(128), nullable=True)
    tf_primary_method = Column(String(64), nullable=True)
    tf_totp_secret = Column(String(255), nullable=True)
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))
    presentations = relationship('Presentation', secondary='presentations_users',
                                 backref=backref('users', lazy='dynamic'))
    # Stripe stuff
    invoices = relationship('Invoice', secondary='invoice_users',
                         backref=backref('users', lazy='dynamic'))
    subscription = relationship('Subscription', secondary='subscription_users',
                         backref=backref('users',lazy='dynamic'))
    stripeCustomerId = Column(String(40), unique=True)