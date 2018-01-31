from flask import flash, redirect, render_template, url_for, current_app, request, abort
from flask_login import login_required
from sqlalchemy.orm import subqueryload
from collections import defaultdict


import os
import re

import logging

from . import metrics
from ..helpers import sysstat
from forms import MetricForm
from app import db
from app.models import Report

logging.debug(dir(sysstat.sysstat))
@metrics.route('/<report_id>', methods=['GET', 'POST'])
@login_required
def display_metrics(report_id):
    report = db.session.query(Report).filter_by(id=report_id).first()
    if report is None:
        abort(404)
    sarfiles = []
    activities = []
    sardir = report.fullpath + "/var/log/sa"
    if os.path.isdir(sardir):
        sarfiles = sysstat.sysstat.get_file_date(sardir)
        activities.extend(sysstat.sysstat.get_stats(file=sarfiles[-1]["filename"], get_metadata="activities"))
        act = []
        for a in activities:
            act.append((a,a))
        form = MetricForm()

    if len(sarfiles) == 0:
        abort(404)
    return render_template('metrics/show.html', form=form, report=report, sarfiles=sarfiles, activities=set(activities))
