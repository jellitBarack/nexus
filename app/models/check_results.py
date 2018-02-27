import hashlib

from app import db

class CheckResult(db.Model):
    """
    Plugins results
    """
    __tablename__ = 'check_results'

    id = db.Column(db.String(32), primary_key=True)
    check_id = db.Column(db.String(32), db.ForeignKey('report_checks.id', ondelete='CASCADE'))
    check = db.relationship("Check", back_populates="check_results")
    hostname = db.Column(db.String(100))
    result_rc = db.Column(db.SmallInteger)
    result_err = db.Column(db.Text)
    result_out = db.Column(db.Text)


    def __init__(self, **kwargs):
         super(CheckResult, self).__init__(**kwargs)
         newid = kwargs.pop('check_id') + kwargs.pop('hostname')
         self.id = str(hashlib.md5(newid.encode('UTF-8')).hexdigest())
    
    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) for (k,v) in vars(self).items()]
        return 'Struct({}\n)'.format(', '.join(args))
