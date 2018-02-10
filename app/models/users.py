from flask_login import UserMixin

from pprint import pformat

from app import db, login_manager

class User(UserMixin, db.Model):
    """
       Create an User table
    """
    __tablename__ = 'users'

    id = db.Column(db.String(32), primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    is_admin = db.Column(db.Boolean, default=False)
    history = db.relationship("History", back_populates="user")

    def __repr__(self):
        return pformat(vars(self))


# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(str(user_id))