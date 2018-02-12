from pprint import pformat
import hashlib

from app import db
import logging

class Check(db.Model):
    """
    Report plugins
    """
    __tablename__ = 'reports_checks'

    id = db.Column(db.String(32), primary_key=True)
    report_id = db.Column(db.String(32), db.ForeignKey('reports_metadata.id', ondelete='CASCADE'))
    report = db.relationship("Report", back_populates="checks" )
    check_results = db.relationship("CheckResult", back_populates="check")
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(50))
    description = db.Column(db.String(250))
    plugin_path = db.Column(db.String(250))
    plugin_id = db.Column(db.String(32))
    backend = db.Column(db.String(50))
    long_name = db.Column(db.String(250))
    bugzilla = db.Column(db.String(250))
    global_rc = db.Column(db.SmallInteger)
    priority = db.Column(db.Integer)
    execution_time = db.Column(db.Numeric(precision=6))

    def __init__(self, **kwargs):
         super(Check, self).__init__(**kwargs)
         plugin_id = kwargs.pop('plugin_id')
         newid = plugin_id + kwargs.pop('report_id')
         self.id = str(hashlib.md5(newid.encode('UTF-8')).hexdigest())
         self.plugin_id = str(hashlib.md5(plugin_id.encode('UTF-8')).hexdigest())

    def __repr__(self):
        return pformat(vars(self))