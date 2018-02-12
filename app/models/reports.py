import datetime
import hashlib

from app import db

class Report(db.Model):
    """
    Reports metadata
    """
    __tablename__ = 'reports_metadata'

    id = db.Column(db.String(32), primary_key=True)
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
        args = ['\n    {} => {}'.format(k, repr(v)) for (k,v) in vars(self).items()]
        return self.__class__.__name__ + '({}\n)'.format(', '.join(args))