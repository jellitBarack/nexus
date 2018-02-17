
from flask import Blueprint

import json
import os
import hashlib
import re

from datetime import datetime
from sqlalchemy import or_


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
    report_id = str(hashlib.md5(
        jsonfile.encode('UTF-8')).hexdigest())

    report = db.session.query(Report).filter(
        or_(Report.md5sum == md5, Report.id == report_id)).first()
    if report is not None and report.id == report_id and md5 == report.md5sum:
        report_changed = False
    elif report is not None:
        report_changed = True
    else:
        report_changed = False

    #report_path = re.sub("^cases\/", "", "/".join(jsonfile.split("/")[-3:]))
    if report is None or report_changed is True:
        # Can't use the path from the metadata because
        # the path is used to generate the unique ID
        # And sometimes, the path is simply . 
        report = Report(
                fullpath=directory,
                source=j["metadata"]["source"],
                live=j["metadata"]["live"],
                path=jsonfile,
                case_id=case_id,
                md5sum=md5,
                analyze_time=datetime.strptime(j["metadata"]["when"], '%Y-%m-%dT%H:%M:%S.%f'),
                analyze_duration=j["metadata"]["time"])
        report.get_report_size()

        # add report to the database
        if report_changed is True:
            db.session.merge(report)
        else:
            db.session.add(report)

        db.session.commit()
        report_changed = True
        


    return report, j["results"], report_changed
