from flask import flash, redirect, render_template, url_for, current_app, request
from flask_login import login_required

from . import reports
from app.models import Report
from app.models import Check

@reports.route('/', methods=['GET', 'POST'])
def display_report():
    return render_template('reports/show.html', report, title='sosreport')


