# Flask
from flask import flash, redirect, render_template, url_for, current_app, request, Response
from flask_login import login_required

# Global imports
import os
import app
import logging
import re
import datetime
from subprocess import Popen, PIPE

# local imports
from . import cases
from forms import CaseSearchForm
from app.models import Report
from app.models import Check
from app import flash_errors
from app import db
from app.checks import loop_checks
from app.reports import add_report
from app.helpers import sysstat



@cases.route('/', methods=['GET', 'POST'])
@login_required
def search():
    """
    Handle requests for cases
    """
    form = CaseSearchForm()
    if form.validate_on_submit():
        casepath = "/cases/" + form.casenum.data
        reportList = []
        jsonregex = []
        combinedregex = re.compile("(" + ")|(".join(current_app.config["REPORT_FILE_NAMES"]) + ")")
        for root, dirs, files in os.walk(casepath, topdown=True):
            matched = filter(combinedregex.match, files)
            if len(matched) > 0:
                for f in matched:
                    fullname = root + "/" + f
                    sardir = root + "/var/log/sa"
                    if os.path.isdir(sardir):
                        sarfiles = sysstat.sysstat.get_file_date(sardir)
                    else:
                        sarfiles = []
                    report_id, results, source, report_changed = add_report(fullname, form.casenum.data)
                    counts = loop_checks(report_id, results, source, report_changed)
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

@cases.route('/compare', methods=['POST','GET'])
@login_required
def compare():
    reports = request.args.getlist("report")
    if len(reports) < 2:
        logging.debug("We need more reports to compare. Got %s reports", reports.length())
        abort(404)
    rlist = []
    for r in reports:
        report = db.session.query(Report).filter_by(id=r).first()
        if report is None:
            logging.debug("Report not found. ID: %s", r)
            abort(404)
        rlist.append(os.path.dirname(report.path))
    logging.debug(rlist)
    outfile = re.match("(/cases/[0-9]+/)", rlist[0]).group(1) + "magui" + str(datetime.datetime.today().strftime('%Y%m%d%H%M%S')) + ".json"
    return Response(magui(outfile, rlist).stderr, mimetype="text/text")

def magui(outfile, reports):
    magui_exec = current_app.config["CITELLUS_PATH"] + "/magui.py"
    args = [magui_exec]
    args.extend(["-o", outfile])
    args.extend(reports)
    logging.debug("Executing %s", args)
    out = Popen(args, stdout=PIPE, stderr=PIPE)
    logging.debug(out)
    return out

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)