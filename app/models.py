
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager
import datetime
import hashlib
import logging
from pprint import pformat

class User(UserMixin, db.Model):
    """
    Create an User table
    """

    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    history = db.relationship("History", backref="parent")

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
    return User.query.get(int(user_id))

class Report(db.Model):
    """
    Reports metadata
    """
    __tablename__ = 'reports_metadata'

    id = db.Column(db.String, primary_key=True)
    source = db.Column(db.String(10))
    live = db.Column(db.Boolean, default=True)
    when = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    execution_time = db.Column(db.SmallInteger)
    path = db.Column(db.String(200))
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

    id = db.Column(db.String, primary_key=True)
    report_id = db.Column(db.String(50), db.ForeignKey('reports_metadata.id'))
    report = db.relationship("Report", back_populates="checks")
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(50))
    description = db.Column(db.String(250))
    plugin_path = db.Column(db.String(250))
    plugin_id = db.Column(db.String(50))
    backend = db.Column(db.String(50))
    long_name = db.Column(db.String(250))
    bugzilla = db.Column(db.String(250))
    result_rc = db.Column(db.SmallInteger)
    result_err = db.Column(db.Text)
    result_out = db.Column(db.Text)
    execution_time = db.Column(db.Numeric(precision=6))

    def __init__(self, **kwargs):
         super(Check, self).__init__(**kwargs)
         newid = kwargs.pop('plugin_id') + kwargs.pop('report_id')
         self.id = str(hashlib.md5(newid.encode('UTF-8')).hexdigest())

    def __repr__(self):
        return pformat(vars(self))

class History(db.Model):
    """
    History for each user
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User")
    item_type = db.Column(db.Integer)
    item_id = db.Column(db.Integer)
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return pformat(vars(self))
