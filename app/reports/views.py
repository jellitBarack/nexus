from flask import flash, redirect, render_template, url_for, current_app, request
from flask_login import login_required
from sqlalchemy.orm import joinedload

import logging

from . import reports
from app import db
from app.models import Report
from app.models import Check

@reports.route('/<report_id>', methods=['GET', 'POST'])
@login_required
def display_report(report_id):
    report = db.session.query(Report).filter_by(id=report_id).options(joinedload('checks')).all()
    #checks = report.checks
    logging.debug(report)
    return render_template('reports/show.html', report=report, title='sosreport')


