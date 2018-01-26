from flask import flash, redirect, render_template, url_for, current_app, request
from flask_login import login_required
from sqlalchemy.orm import subqueryload
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

import logging

from . import reports
from app import db
from app.models import Report
from app.models import Check

@reports.route('/<report_id>', methods=['GET', 'POST'])
@login_required
def display_report(report_id):
    report = db.session.query(Report).filter_by(id=report_id).options(subqueryload('checks')).first()
    #logging.debug(report)

    # Getting a list of categories
    categories = defaultdict(int)
    for c in report.checks:
        categories[c.category] += 1
        if c.subcategory != "":
            subcategories = c.subcategory.split("/")
        else:
            subcategories = []
        c.subcategory = subcategories
        if c.category not in subcategories:
            subcategories.insert(0, c.category)
        c.all_categories = subcategories
        c.plugin_html = current_app.config["PLUGIN_STATES"][c.result_rc]
        c.plugin_name = os.path.splitext(os.path.basename(c.plugin_path))[0]
        logging.debug(c)
        if not hasattr(c, 'priority'):
            c.priority = 0
            c.priority_text = "info"

        if c.priority >= 666:
            c.priority_text = "critical"
            c.priority_class = "danger"
        elif c.priority >= 333:
            c.priority_text = "important"
            c.priority_class = "warning"
        else:
            c.priority_text = "informative"
            c.priority_class = "info"
            
        if re.match('^\d{7}$', c.plugin_name):
            c.bug_id = c.plugin_name
            c.bugzilla = "https://bugzilla.redhat.com/show_bug.cgi?id=" + str(c.bug_id)
        else:
            try:
                m = re.search('([0-9]+$)', c.bugzilla)
                c.bug_id = m.group(0)
            except:
                pass
        

        for s in subcategories:
            categories[s] += 1


    
    return render_template('reports/show.html', report=report, categories=categories, title='sosreport')


