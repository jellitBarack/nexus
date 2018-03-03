import datetime
import hashlib

from app import db

"""
alter table history modify item_id varchar(32)
alter table history modify item_type varchar(32)
alter table history add column action varchar(16) after user_id;
"""


class History(db.Model):
    """
    History for each user
    """
    id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship("User", back_populates="history")
    action = db.Column(db.String(16))
    item_type = db.Column(db.Integer)
    item_id = db.Column(db.String(32))
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    report_name = ""
    report_date = ""
    action_link = ""

    def __init__(self, **kwargs):
        super(History, self).__init__(**kwargs)
        string = str(datetime.datetime.utcnow) + self.action + self.item_type + str(self.user_id) + str(self.item_id)
        self.id = hashlib.md5(string.encode('UTF-8')).hexdigest()
        self.get_link()

    def get_link(self):
        if self.action == "yank" or self.action == "show":
            self.action_link = "cases.search"
        elif self.action == "network":
            self.action_link = "network.display_network"
        elif self.action == "metrics":
            self.action_link = "metrics.display_metrics"
        elif self.action == "health":
            self.action_link = "health.display_health"
        elif self.action == "checks":
            self.action_link = "reports.display_checks"

    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) for (k, v) in vars(self).items()]
        return self.__class__.__name__ + '({}\n)'.format(', '.join(args))
