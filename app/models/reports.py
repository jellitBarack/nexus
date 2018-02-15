import datetime
import hashlib
from subprocess import check_output

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
    #verification_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    when = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    #collect_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    #execution_duration = db.Column(db.SmallInteger)
    execution_time = db.Column(db.SmallInteger)
    #size = db.Column(db.Integer)
    path = db.Column(db.String(200))
    #machine_id = db.Column(db.String(50))
    md5sum = db.Column(db.String(200))
    case_id = db.Column(db.Integer)
    checks = db.relationship("Check", back_populates="report")

    def __init__(self, **kwargs):
         super(Report, self).__init__(**kwargs)
         self.id = str(hashlib.md5(kwargs.pop('path').encode('UTF-8')).hexdigest())

    def generate_id(self, path):
        return hashlib.md5(path.encode('UTF-8')).hexdigest()

    def get_machine_id(self):
        try:
            out = check_output('grep -oP --color=never "UUID: \K(.*)" ' + self.path + 'dmidecode', shell=True)
        except CalledProcessError:
            out = ""
        self.machine_id = out
        logging.debug("Executing %s", args)
        out = Popen(args, stdout=PIPE, stderr=PIPE)
        logging.debug(out)
    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) for (k,v) in vars(self).items()]
        return self.__class__.__name__ + '({}\n)'.format(', '.join(args))
