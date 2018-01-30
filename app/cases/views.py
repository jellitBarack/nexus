# Flask
from flask import flash, redirect, render_template, url_for, current_app, request
from flask_login import login_required

# Global imports
import os
import app
import logging

# local imports
from . import cases
from forms import CaseSearchForm
from app.models import Report
from app.models import Check
from app import flash_errors
from app import db
from app.checks import loop_checks
from app.reports import add_report



@cases.route('/', methods=['GET', 'POST'])
def search():
    """
    Handle requests for cases
    """
    form = CaseSearchForm()
    if form.validate_on_submit():
        casepath = "/cases/" + form.casenum.data
        reportList = []
        for root, dirs, files in os.walk(casepath, topdown=True):
            for f in current_app.config["REPORT_FILE_NAMES"]:
                if f in files:
                    sarfiles = []
                    fullname = root + "/" + f
                    sardir = root + "/var/log/sa/"
                    if os.path.isdir(sardir):
                        for saroot, sadirs, sarfilelist in os.walk(sardir, topdown=True):
                            for sarfile in sarfilelist:
                                sarfiles.append(saroot + sarfile)
                    sarfiles.sort(key=lambda x: os.path.getmtime(x))
                    report_id, results, source = add_report(fullname, form.casenum.data)
                    counts = loop_checks(report_id, results, source)
                    # add report to the web interface
                    if source == "magui":
                        icon = "microchip"
                    else:
                        icon = "cog"
                    reportList.append({"fullname": fullname, 
                                "name": "/".join(root.split("/")[-2:]), 
                                "report_id": report_id,
                                "icon": icon, 
                                "sarfiles": sarfiles,
                                "checks_total": counts["total"], 
                                "checks_fail": counts[20], 
                                "checks_skip": counts[30], 
                                "checks_okay": counts[10], 
                                "execution_time": 0,
                                "source": source})

            if root.count(os.sep) - casepath.count(os.sep) == 2:
                del dirs[:]

        return render_template('cases/search.html', form=form, reportList=reportList, title='Search sosreport in case')
    elif request.method == "POST":
        flash_errors(form)
    return render_template('cases/search.html', form=form, title='Search sosreport in case')

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)