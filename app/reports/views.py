from flask import render_template, current_app, request, abort
from flask_login import login_required
from sqlalchemy.orm import subqueryload, contains_eager
from collections import defaultdict

import os
import re

"""
http://docs.sqlalchemy.org/en/latest/orm/loading_relationships.html#what-kind-of-loading-to-use
When using subquery loading, the load of 100 objects will emit two SQL statements.
The second statement will fetch a total number of rows equal to the sum of the size of all collections.
An INNER JOIN is used, and a minimum of parent columns are requested, only the primary keys.
So a subquery load makes sense when the collections are larger.
"""

from . import reports
from app import db
from app.models import Report
from app.models import Check


@reports.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    return render_template('layout/not-ready.html')


@reports.route('/history', methods=['GET', 'POST'])
@login_required
def history():
    return render_template('layout/not-ready.html')


# placeholder route to allow the creation of /reports/ url
@reports.route('/', methods=['GET'])
@login_required
def index():
    return render_template('layout/not-ready.html')


@reports.route('/<report_id>/metrics', methods=['GET', 'POST'])
@login_required
def display_metrics(report_id):
    return render_template('layout/not-ready.html')


@reports.route('/<report_id>/compare', methods=['GET', 'POST'])
@login_required
def compare(report_id):
    return render_template('layout/not-ready.html')


@reports.route('/<report_id>/checks', methods=['GET', 'POST'])
@login_required
def display_checks(report_id, rc=None):
    rc = request.args.get('rc')
    # Getting the checks from the DB
    q = db.session.query(Report).join(Check, Report.checks).options(contains_eager(Report.checks))
    report_name = "show"

    if rc is not None:
        q = q.filter(Check.global_rc == rc)
        report_name = "list"

    q = q.filter(Report.id == report_id).order_by(Check.priority.desc())
    report = q.options(subqueryload('checks', 'check_results')).all()
    if report is None or len(report) == 0:
        abort(404)
    # Getting a list of categories
    categories = defaultdict(int)
    for c in report[0].checks:
        # Building the categories dict
        categories[c.category] += 1
        subcategories = []
        if c.subcategory != "":
            subcategories = c.subcategory.split("/")
        c.subcategory = subcategories
        if c.category not in subcategories:
            subcategories.insert(0, c.category)
        c.all_categories = subcategories
        for s in subcategories:
            categories[s] += 1

        # Building the visual for the plugin state
        c.plugin_html = current_app.config["PLUGIN_STATES"][c.global_rc]
        c.plugin_name = os.path.splitext(os.path.basename(c.plugin_path))[0]

        # Building the visual for the plugin priority
        c.priority_text = "informative"
        c.priority_class = "info"
        if not hasattr(c, 'priority'):
            c.priority = 0
        if c.priority >= 666:
            c.priority_text = "critical"
            c.priority_class = "danger"
        elif c.priority >= 333:
            c.priority_text = "important"
            c.priority_class = "warning"

        # Extracting the bugzilla informations
        if re.match('^\d{7}$', c.plugin_name):
            c.bug_id = c.plugin_name
            c.bugzilla = "https://bugzilla.redhat.com/show_bug.cgi?id=" + str(c.bug_id)
        else:
            try:
                m = re.search('([0-9]+$)', c.bugzilla)
                c.bug_id = m.group(0)
            except:
                pass
    return render_template('reports/' + report_name + '.html', report=report[0], categories=categories,
                           title='sosreport')
