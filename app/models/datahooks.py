import hashlib

from app import db


class Datahook(db.Model):
    """
    Datahook
    """
    __tablename__ = 'datahooks'

    id = db.Column(db.String(32), primary_key=True)
    check_id = db.Column(db.String(32), db.ForeignKey('report_checks.id', ondelete='CASCADE'))
    check = db.relationship("Check", back_populates="datahooks")
    event = db.Column(db.String(20))
    rc = db.Column(db.SmallInteger)
    err = db.Column(db.Text)
    out = db.Column(db.Text)

    def __init__(self, **kwargs):
        super(Datahook, self).__init__(**kwargs)
        newid = kwargs.pop('check_id') + kwargs.pop('event')
        self.id = str(hashlib.md5(newid.encode('UTF-8')).hexdigest())

    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return 'Struct({}\n)'.format(', '.join(args))
