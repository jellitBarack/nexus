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


def add_report(report):
    """
    Assemble the information from the json file
    and the metadata we had already.
    It the stores the report in the DB
    :param report: object that was previously scanned
    :return: report object, results list, and if report has changed
    """
    j = json.load(open(report.fullpath))
    report.md5sum = hashlib.md5(open(report.fullpath, 'rb').read()).hexdigest()

    if j["metadata"]["source"] == "magui":
        j["metadata"]["live"] = False
    if j["metadata"].has_key("time") is False:
        j["metadata"]["time"] = 0

    report_db = db.session.query(Report).filter(
        or_(Report.md5sum == report.md5sum, Report.id == report.id)).first()

    report.changed = False
    if report_db is not None and report_db.md5sum == report.md5sum:
        report.changed = False
    elif report_db is not None:
        report.changed = True

    report.setattrs(source=j["metadata"]["source"],
                    live=j["metadata"]["live"],
                    analyze_time=datetime.strptime(j["metadata"]["when"], '%Y-%m-%dT%H:%M:%S.%f'),
                    analyze_duration=round(j["metadata"]["time"], 3))

    if report_db is None or report.changed is True:
        report.get_report_size()
        # add report to the database
        if report.changed is True:
            db.session.merge(report)
        else:
            db.session.add(report)

        db.session.commit()
        report.changed = True
    elif report_db is not None and report.changed is False:
        report.size = report_db.size

    report.results = j["results"]
