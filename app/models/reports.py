import datetime
import hashlib
import re
import logging
import os

from subprocess import check_output, CalledProcessError

from app import db

class Report(db.Model):
    """
    Reports metadata
    """
    __tablename__ = 'reports_metadata'

    """
    ALTER TABLE reports_metadata add column collect_time datetime after live;
    ALTER TABLE reports_metadata ADD COLUMN machine_id VARCHAR(50)
    ALTER TABLE reports_metadata ADD COLUMN name VARCHAR(100) after fullpath;
    ALTER TABLE reports_metadata ADD COLUMN `size` bigint unsigned AFTER path;
    ALTER TABLE reports_metadata CHANGE COLUMN `when` `analyze_time` datetime after `collect_time`;
    ALTER TABLE reports_metadata CHANGE COLUMN `execution_time` `analyze_duration` decimal(6,3) after  analyze_time;
    """

    id = db.Column(db.String(32), primary_key=True)
    fullpath = db.Column(db.String(200))
    source = db.Column(db.String(10))
    live = db.Column(db.Boolean, default=True)
    collect_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    analyze_duration = db.Column(db.Numeric(6,3))
    analyze_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    size = db.Column(db.Integer)
    path = db.Column(db.String(200))
    machine_id = db.Column(db.String(50))
    md5sum = db.Column(db.String(200))
    case_id = db.Column(db.Integer)
    checks = db.relationship("Check", back_populates="report")
    name = db.Column(db.String(100))
    sarfiles = ""
    def __init__(self, **kwargs):
        super(Report, self).__init__(**kwargs)
        try:
           self.fullpath = kwargs.pop('fullpath')
        except KeyError:
           return
        report_name = "/".join(self.fullpath.split("/")[-2:])
        self.id = self.generate_id(self.fullpath)
        self.path = os.path.dirname(os.path.abspath(self.fullpath))
        self.name = "/".join(self.fullpath.split("/")[-2:]),
        self.get_machine_id()
        self.get_collect_time()

    def setattrs(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)

    def generate_id(self, path):
        """
        Generates an id 
        :param path:  jsonfile path
        :return: md5sum
        """
        return hashlib.md5(path.encode('UTF-8')).hexdigest()

    def get_machine_id(self):
        """
        Try to find system uuid in dmidecode
        :return: save machine_id to object
        """
        try:
            out = check_output('grep -oP --color=never "UUID: \K([^\s]+)" ' + self.path + '/dmidecode', shell=True)
        except CalledProcessError:
            out = ""
        self.machine_id = out.rstrip()

    def get_report_size(self):
        """
        Returns the size of the full sosreport folder
        :return size: size in bytes
        """
        try:
            out = re.search('^([0-9]+)', check_output('du -sb ' + self.path, shell=True)).group(1)
        except CalledProcessError:
            out = ""  
        self.size =  int(out)

    def get_hr_size(self, precision=2):
        """
        Translates self.size in a human readable format
        :param precision: to round the number
        :return: human readable format
        """
        suffixes=['B','KB','MB','GB','TB']
        suffix_index = 0
        hr_size = self.size
        while hr_size > 1024 and suffix_index < 4:
            suffix_index += 1 #increment the index of the suffix
            hr_size = hr_size/1024.0 #apply the division
        return "%.*f%s"%(precision,hr_size,suffixes[suffix_index])

    def get_collect_time(self):
        """
        Get the report collection time
        :return datetime about the date of the report
        """
        try:
            with open(self.path + '/date', "r") as f:
                date = f.readlines()
            cdate = datetime.datetime.strptime(re.sub(' +',' ',date[0]),
                                                '%a %b %d %H:%M:%S %Z %Y\n')
        except:
            cdate = datetime.datetime.now()
        self.collect_time = cdate

    def __repr__(self):
        args = ['\n    {} => {}'.format(k, repr(v)) 
                for (k,v) in vars(self).items()]
        return self.__class__.__name__ + '({}\n)'.format(', '.join(args))
