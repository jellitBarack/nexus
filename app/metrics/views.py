from flask import flash, redirect, render_template, url_for, current_app, request, abort, jsonify
from flask_login import login_required
from sqlalchemy.orm import subqueryload
from collections import defaultdict
from datetime import datetime


import os
import re
import json

import logging

from . import metrics
from ..helpers import sysstat
from app import db
from app.models import Report

@metrics.route('/<report_id>', methods=['GET'])
@login_required
def display_metrics(report_id):
    report = get_report(report_id)
    sarfiles, activities = get_metadata(report,"activities")

    if len(sarfiles) == 0:
        abort(404)
    return render_template('metrics/show.html', report=report, sarfiles=sarfiles, activities=set(activities))

@metrics.route('/<report_id>/keys', methods=['GET'])
@login_required
def get_keys(report_id):
    """
    This function is called by ajax calls. 
    :returns keys for a specific activity
    """
    activity = request.args.get('activity')
    report = get_report(report_id)
    sarfiles, keys = get_metadata(report, "keys", activity)
      
    return jsonify(keys)

@metrics.route('/<report_id>/points', methods=['POST'])
@login_required
def get_points(report_id):
    """
    This function is called by ajax calls. 
    :returns sets of points matching criteria
    """
    data = json.loads(request.data)
    logging.debug(data)
    report = get_report(report_id)
    sardir = report.fullpath + "/var/log/sa"
    fullstats = []
    if os.path.isdir(sardir):
        sarfiles = sysstat.sysstat.get_file_date(sardir, datetime.strptime(data["startDate"], '%Y-%m-%d %H:%M:%S'), datetime.strptime(data["endDate"], '%Y-%m-%d %H:%M:%S'))
        for file in sarfiles:
            stats = sysstat.sysstat.get_stats(file=file["filename"], get_metadata=None, activity=data["activity"], 
            data_type=data["activity"], start_date=datetime.strptime(data["startDate"], '%Y-%m-%d %H:%M:%S'), end_date=datetime.strptime(data["endDate"], '%Y-%m-%d %H:%M:%S'), 
            filter_list=data["filters"], filter_condition="and")
            fullstats.append(stats)
    return jsonify(fullstats)

def get_metadata(report, get_metadata, activity=None):
    sarfiles = []
    metadata = []
    sardir = report.fullpath + "/var/log/sa"
    if os.path.isdir(sardir):
        sarfiles = sysstat.sysstat.get_file_date(sardir)
        metadata.extend(sysstat.sysstat.get_stats(file=sarfiles[-1]["filename"], get_metadata=get_metadata, activity=activity))
        return sarfiles, metadata
    return None


def get_report(report_id):
    report = db.session.query(Report).filter_by(id=report_id).first()
    if report is None:
        abort(404)
    return report