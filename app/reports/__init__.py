
from flask import Blueprint

import json
import os
from datetime import datetime


reports = Blueprint('reports', __name__)

from . import views
from app import db
from app.models import Report

def add_report(jsonfile, case_id):
    j = json.load(open(jsonfile))
    directory = os.path.dirname(os.path.abspath(jsonfile))
    if j["metadata"]["source"] == "magui":
        j["metadata"]["live"] = False
    if j["metadata"].has_key("time") is False:
        j["metadata"]["time"] = 0
    # Can't use the path from the metadata because
    # the path is used to generate the unique ID
    # And sometimes, the path is simply . 
    report = Report(source=j["metadata"]["source"],
                live=j["metadata"]["live"],
                path="/".join(jsonfile.split("/")[-3:]),
                when=datetime.strptime(j["metadata"]["when"], '%Y-%m-%dT%H:%M:%S.%f'),
                case_id=case_id,
                execution_time=j["metadata"]["time"])
    # add report to the database
    db.session.merge(report)
    db.session.commit()

    return report.id, j["results"], report.source