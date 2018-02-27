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
from app.checks import loop_checks, count_checks
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
        command = "/bin/bash /usr/bin/yank " + case + "--force "
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
        report_list = []
        # Folder doesn't exist, let's check the DB
        if os.path.isdir(casepath) is False:
            report_list = Report.query.filter(Report.case_id == case).all()
            if report_list is None or len(report_list) == 0:
               return render_template('cases/notfound.html', casenum = case), 404
        else:
            report_list = find_reports(casepath, case)
            # We prepare to delete in case report has changed.
            report_delete = []
            for report in report_list:
                add_report(report)
                if report.changed is True:
                    report_delete.append(report.id)

            # To make things faster, we need to bulk delete the 
            # checks for the reports that have changed.
            if len(report_delete) > 0:
                Check.query.filter(Check.report_id.in_(report_delete)).delete(synchronize_session=False)

        for report in report_list:
            loop_checks(report)
            count = count_checks(report.id)
            # add report to the web interface
            report.icon = "cog"
            if report.source == "magui":
                report.icon = "microchip"
            report.setattrs(
                            checks_total = count["total"],
                            checks_fail = count[current_app.config["RC_FAILED"]], 
                            checks_skip = count[current_app.config["RC_SKIPPED"]], 
                            checks_okay = count[current_app.config["RC_OKAY"]])

            if report.changed is True:
                report.hr_size = report.get_hr_size()
    
        return render_template('cases/search.html', form = form, casenum = case, report_list = report_list)
    # There was an error with the form submission
    elif request.method == "POST":
        flash_errors(form)
    # If no caseid, we return standard form
    return render_template('cases/search.html')

def find_reports(path, case):
    """
    Look for reports in path
    :param path: Path of extracted sosreport
    :param case: case id
    :return reports: list of Reports
    """
    report_list = []
    combinedregex = re.compile("(" + ")|(".join( current_app.config["REPORT_FILE_NAMES"]) + ")")
    for root, dirs, files in os.walk(path, topdown=True):
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

            report = Report(fullpath=root + "/" + f,
                            case_id=case,
                            sarfiles=sarfiles)
            report_list.append(report)

        # We don't go deeper than 2 directories
        # to save some time
        if root.count(os.sep) - path.count(os.sep) == 2:
            del dirs[:]

    return report_list
    
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
