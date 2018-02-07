
from flask import Blueprint

import json
import os
import hashlib
import re

from datetime import datetime


reports = Blueprint('reports', __name__)

from . import views
from app import db
from app.models import Report
import logging

def add_report(jsonfile, case_id):
    j = json.load(open(jsonfile))
    directory = os.path.dirname(os.path.abspath(jsonfile))
    if j["metadata"]["source"] == "magui":
        j["metadata"]["live"] = False
    if j["metadata"].has_key("time") is False:
        j["metadata"]["time"] = 0
    md5 = hashlib.md5(open(jsonfile, 'rb').read()).hexdigest()
    report = db.session.query(Report).filter_by(md5sum=md5).first()
    report_changed = False
    #report_path = re.sub("^cases\/", "", "/".join(jsonfile.split("/")[-3:]))
    if report is None:
        # Can't use the path from the metadata because
        # the path is used to generate the unique ID
        # And sometimes, the path is simply . 
        report = Report(
                fullpath=directory,
                source=j["metadata"]["source"],
                live=j["metadata"]["live"],
                path=jsonfile,
                when=datetime.strptime(j["metadata"]["when"], '%Y-%m-%dT%H:%M:%S.%f'),
                case_id=case_id,
                md5sum=md5,
                execution_time=j["metadata"]["time"])
        # add report to the database
        db.session.merge(report)
        db.session.commit()
        report_changed = True
        


    return report.id, j["results"], report.source, report_changed