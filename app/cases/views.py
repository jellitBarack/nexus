# Flask
from flask import flash, redirect, render_template, url_for
from flask import current_app, request, abort, jsonify
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


@cases.route('/<case>/yank?force=<force>')
@cases.route('/<case>/yank')
@login_required
def yank(case, force=None):
    """
    Yank files to collab-shell
    :param case: case id
    :param force: if true, we force the yank
    :return: redirect to /cases/caseid
    """
    if force == 'True':
        command = "/bin/bash /usr/bin/yank --force " + case
    else:
        command = "/bin/bash /usr/bin/yank " + case
    try:
        result = subprocess.check_output([command], shell=True)
    except subprocess.CalledProcessError as e:
        flash(u"Unable to yank case %s: %s" % (case,e.output),
              category="error")
    return redirect(url_for("cases.search", case=case), 303)


@cases.route('/', methods=['GET', 'POST'])
@cases.route('/<case>', methods=['GET'])
@login_required
def search(case=None):
    """
    Handle requests for cases
    :param case: case id
    :return: search.html
    """

    form = CaseSearchForm()
    if case is None and form.validate_on_submit():
        case = form.casenum.data
    if case is not None:
        casepath = "/cases/" + case
        reportList = []
        jsonregex = []
        # Building regex for citellus[0-9]+.json and magui[0-9]+.json
        combinedregex = re.compile("(" + ")|(".join(
                                       current_app.config["REPORT_FILE_NAMES"])
                                    + ")")
        if os.path.isdir(casepath) is False:
            abort(404)
        # Looping through the files
        for root, dirs, files in os.walk(casepath, topdown=True):
            matched = filter(combinedregex.match, files)
            if len(matched) == 0:
                continue
            for f in matched:
                fullname = root + "/" + f
                sardir = root + "/var/log/sa"
                if os.path.isdir(sardir):
                    sarfiles = sysstat.sysstat.get_file_date(sardir)
                else:
                    sarfiles = []
                report, results, report_changed = add_report(fullname, form.casenum.data)
                counts = loop_checks(report.id, results, report.source, report_changed)
                # add report to the web interface
                if report.source == "magui":
                    icon = "microchip"
                else:
                    icon = "cog"
                reportList.append({"fullname": fullname,
                            "name": "/".join(root.split("/")[-2:]), 
                            "report_id": report.id,
                            "icon": icon, 
                            "sarfiles": sarfiles,
                            "checks_total": counts["total"], 
                            "checks_fail": counts[20], 
                            "checks_skip": counts[30], 
                            "checks_okay": counts[10], 
                            "analyze_duration": report.analyze_duration,
                            "size": report.size,
                            "hr_size": report.get_hr_size(2),
                            "collect_time": report.collect_time,
                            "machine_id": report.machine_id,
                            "source": report.source})
    
        # We don't go deeper than 2 directories
        # to save some time
        if root.count(os.sep) - casepath.count(os.sep) == 2:
            del dirs[:]
    
        return render_template('cases/search.html', form=form, casenum = case, 
                           reportList = reportList, 
                           title = 'Search sosreport in case')
    # There was an error with the form submission
    elif request.method == "POST":
        flash_errors(form)
    # If no caseid, we return standard form
    return render_template('cases/search.html')

@cases.route('/compare', methods=['POST','GET'])
@login_required
def compare():
    """
    Compare multiple reports
    :param json: array of report ids
    :return: json object: status, msg
    """
    reports = request.get_json()
    if len(reports) < 2:
        return jsonify({ "status": "danger",
                        "msg": "We need at least 2 reports to compare"})
    rlist = []
    for r in reports:
        report = db.session.query(Report).filter_by(id=r).first()
        if report is None:
            return jsonify({ "status": "danger", "msg": "Report not found" })
        rlist.append(os.path.dirname(report.path))
    outfile = re.match("(/cases/[0-9]+/)", rlist[0]).group(1) + "magui" \
              + str(datetime.datetime.today().strftime('%Y%m%d%H%M%S')) + ".json"
    return magui(outfile, rlist)

def magui(outfile, reports):
    """
    Runs magui (compare tool) on reports
    :param outfile: json output file generated by magui
    :param reports: list of report ids
    :return: json object with execution status
    """
    args = ["python", current_app.config["CITELLUS_PATH"] + "/magui.py"]
    args.extend(["--loglevel", "DEBUG", "-o", outfile])
    args.extend(reports)
    command = " ".join(args)
    try:
        result = subprocess.check_output([command], shell=True)
    except subprocess.CalledProcessError as e:
        return jsonify({ "status": "danger", 
                        "msg": "An error occurred while executing command."})
    return jsonify({ "status": "success", 
                    "msg": "Succesfully generated compare report"})
