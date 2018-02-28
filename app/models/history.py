import datetime

from app import db


class History(db.Model):
    """
    History for each user
    """
    id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship("User", back_populates="history")
    item_type = db.Column(db.Integer)
    item_id = db.Column(db.Integer)
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return self.__class__.__name__ + '({}\n)'.format(', '.join(args))
