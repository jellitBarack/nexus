
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager
from config import Config as conf
import datetime
import hashlib
import logging

from pprint import pformat
"""
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import entity
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config
"""
# https://github.com/mitsuhiko/flask-openid/blob/master/example/example.py

class Client(db.Model):
    """
    A client is the app which wants to use the resource of a user. It is suggested that the client is registered 
    by a user on your site, but it is not required.

    The client should contain at least these properties:

        client_id: A random string
        client_secret: A random string
        client_type: A string represents if it is confidential
        redirect_uris: A list of redirect uris
        default_redirect_uri: One of the redirect uris
        default_scopes: Default scopes of the client
        But it could be better, if you implemented:

        allowed_grant_types: A list of grant types
        allowed_response_types: A list of response types
        validate_scopes: A function to validate scopes
    """
    # human readable name, not required
    name = db.Column(db.String(40))

    # human readable description, not required
    description = db.Column(db.String(400))

    # creator of the client, not required
    user_id = db.Column(db.ForeignKey('users.id'))
    # required if you need to support client credential
    user = db.relationship('User')

    client_id = db.Column(db.String(50), primary_key=True)
    client_secret = db.Column(db.String(55), unique=True, index=True,
                              nullable=False)

    # public or confidential
    is_confidential = db.Column(db.Boolean)

    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

class Grant(db.Model):
    """
    A grant token is created in the authorization flow, and will be destroyed when the authorization is finished. 
    In this case, it would be better to store the data in a cache, which leads to better performance.
    A grant token should contain at least this information:

        client_id: A random string of client_id
        code: A random string
        user: The authorization user
        scopes: A list of scope
        expires: A datetime.datetime in UTC
        redirect_uri: A URI string
        delete: A function to delete itself

    """
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.String(30), db.ForeignKey('users.id', ondelete='CASCADE')
    )
    user = db.relationship('User')

    client_id = db.Column(
        db.String(50), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

class Token(db.Model):
    """
    A bearer token is the final token that could be used by the client. There are other token types, but bearer token is widely used. Flask-OAuthlib only comes with a bearer token.

    A bearer token requires at least this information:
        access_token: A string token
        refresh_token: A string token
        client_id: ID of the client
        scopes: A list of scopes
        expires: A datetime.datetime object
        user: The user object
        delete: A function to delete itself

    """
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(50), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    user_id = db.Column(
        db.String(30), db.ForeignKey('users.id')
    )
    user = db.relationship('User')

    # currently only bearer is supported
    token_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []
class User(UserMixin, db.Model):
    """
       Create an User table
    """
    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'users'

    id = db.Column(db.String(30), primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    is_admin = db.Column(db.Boolean, default=False)
    history = db.relationship("History", back_populates="user")

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """

        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """

        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """

        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return pformat(vars(self))


# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(str(user_id))

class Report(db.Model):
    """
    Reports metadata
    """
    __tablename__ = 'reports_metadata'

    id = db.Column(db.String(30), primary_key=True)
    fullpath = db.Column(db.String(200))
    source = db.Column(db.String(10))
    live = db.Column(db.Boolean, default=True)
    when = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    execution_time = db.Column(db.SmallInteger)
    path = db.Column(db.String(200))
    md5sum = db.Column(db.String(200))
    case_id = db.Column(db.Integer)
    checks = db.relationship("Check", back_populates="report")

    def __init__(self, **kwargs):
         super(Report, self).__init__(**kwargs)
         self.id = str(hashlib.md5(kwargs.pop('path').encode('UTF-8')).hexdigest())
       
    def generate_id(self, path):
        return hashlib.md5(path.encode('UTF-8')).hexdigest()

    def __repr__(self):
        return pformat(vars(self))

 

class Check(db.Model):
    """
    Report plugins
    """
    __tablename__ = 'reports_checks'

    id = db.Column(db.String(30), primary_key=True)
    report_id = db.Column(db.String(30), db.ForeignKey('reports_metadata.id'))
    report = db.relationship("Report", back_populates="checks")
    check_results = db.relationship("CheckResults", back_populates="check")
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(50))
    description = db.Column(db.String(250))
    plugin_path = db.Column(db.String(250))
    plugin_id = db.Column(db.String(50))
    backend = db.Column(db.String(50))
    long_name = db.Column(db.String(250))
    bugzilla = db.Column(db.String(250))
    global_rc = db.Column(db.SmallInteger)
    priority = db.Column(db.Integer)
    execution_time = db.Column(db.Numeric(precision=6))

    def __init__(self, **kwargs):
         super(Check, self).__init__(**kwargs)
         newid = kwargs.pop('plugin_id') + kwargs.pop('report_id')
         self.id = str(hashlib.md5(newid.encode('UTF-8')).hexdigest())

    def __repr__(self):
        return pformat(vars(self))  

class CheckResults(db.Model):
    """
    Plugins results
    """
    __tablename__ = 'check_results'

    id = db.Column(db.String(30), primary_key=True)
    check_id = db.Column(db.String(30), db.ForeignKey('reports_checks.id'))
    check = db.relationship("Check", back_populates="check_results")
    hostname = db.Column(db.String(100))
    result_rc = db.Column(db.SmallInteger)
    result_err = db.Column(db.Text)
    result_out = db.Column(db.Text)


    def __init__(self, **kwargs):
         super(CheckResults, self).__init__(**kwargs)
         newid = kwargs.pop('check_id') + kwargs.pop('hostname')
         self.id = str(hashlib.md5(newid.encode('UTF-8')).hexdigest())

    def __repr__(self):
        return pformat(vars(self))

class History(db.Model):
    """
    History for each user
    """
    id = db.Column(db.String(30), primary_key=True)
    user_id = db.Column(db.String(30), db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates="history")
    item_type = db.Column(db.Integer)
    item_id = db.Column(db.Integer)
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return pformat(vars(self))
