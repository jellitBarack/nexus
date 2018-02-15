# Flask
from flask import flash, redirect, render_template, url_for, current_app, request, Response, abort
from flask_login import login_required

# Global imports
import os
import app
import logging
import re
import datetime
import subprocess

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
@cases.route('/?case=<case>&yank=<yank>', methods=['GET', 'POST'])
@cases.route('/?case=<case>&yank=<yank>&force=<force>', methods=['GET', 'POST'])
@login_required
def search(case=None, yank=None, force=None):
    """
    Handle requests for cases
    """
    def yank(case, force=None):
        if force == 'True':
            command = "/bin/bash /usr/bin/yank --force " + case
        elif force is None:
            command = "/bin/bash /usr/bin/yank " + case

        logging.debug("searching for attachment for case %s", case)
        logging.debug("executing command: %s", command)
        try:
            result = subprocess.check_output([command], shell=True)
        except subprocess.CalledProcessError as e:
            return "An error occurred while executing command."

    form = CaseSearchForm()
    if case is None and form.validate_on_submit():
        case = form.casenum.data
    elif yank is not None and case is not None:
        yank(case, force)
    if case is not None:
        casepath = "/cases/" + case
        reportList = []
        jsonregex = []
        combinedregex = re.compile("(" + ")|(".join(current_app.config["REPORT_FILE_NAMES"]) + ")")
        #du -s /cases/02031310/sosreport-20180209-033909/wcmsc5-l-rh-ocld-0
        #1955016	/cases/02031310/sosreport-20180209-033909/wcmsc5-l-rh-ocld-2
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
    reports = request.get_json()
    if len(reports) < 2:
        logging.debug("We need more reports to compare. Got %s reports", len(reports))
        abort(400)
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
    args = ["python", current_app.config["CITELLUS_PATH"] + "/magui.py"]
    args.extend(["--loglevel", "DEBUG", "-o", outfile])
    #args = ["ls", "-l"]
    args.extend(reports)
    logging.debug("Executing %s", args)
    #p = Popen(args, stdout=PIPE, stderr=PIPE, bufsize=1)
    #for line in iter(p.stdout.readline, b''):
    #    logging.debug(line)
    #p.stdout.close()
    #p.wait()
    return None

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)
