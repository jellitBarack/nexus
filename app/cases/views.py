# Flask
from flask import flash, redirect, render_template, url_for
from flask import current_app, request, jsonify
from flask_login import login_required

# Global imports
import os
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
from app.checks.helper import loop_checks, count_checks
from app.reports.helper import add_report
from app.helpers.history import create_event
from app.cases.helper import find_reports, magui


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
    create_event("yank", "case", [case])
    case = re.sub('^[0]*', '0', str(case))
    if force == 'True':
        command = "/bin/bash /usr/bin/yank " + case + " --force "
    else:
        command = "/bin/bash /usr/bin/yank " + case
    try:
        subprocess.check_output([command], shell=True)
    except subprocess.CalledProcessError as e:
        flash(u"Unable to yank case %s: %s" % (case, e.output),
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
        casepath = current_app.config["CASES_PATH"] + "/" + case
        report_list = []
        # Folder doesn't exist, let's check the DB
        create_event("show", "case", [case])
        if os.path.isdir(casepath) is False:
            report_list = Report.query.filter(Report.case_id == case).all()
            if report_list is None or len(report_list) == 0:
                return render_template('cases/notfound.html', casenum=case), 404
            else:
                flash(u"Files for case %s are not found, but we have cached the metadata" % (case), category="warning")
        else:
            report_list = find_reports(casepath, case, current_app.config["REPORT_FILE_NAMES"])
            # We prepare to delete in case report has changed.
            report_delete = []
            for report in report_list:
                add_report_status = add_report(report)
                if report.changed is True:
                    report_delete.append(report.id)
                if add_report_status is not None:
                    return render_template('errors/generic-error.html', message=report.fullpath + ": " + add_report_status), 403

            # To make things faster, we need to bulk delete the
            # checks for the reports that have changed.
            if len(report_delete) > 0:
                Check.query.filter(Check.report_id.in_(report_delete)).delete(synchronize_session=False)

        for report in report_list:
            loop_checks(report, current_app)
            count = count_checks(report.id)
            # add report to the web interface
            report.icon = "cog"
            if report.source == "magui":
                report.icon = "microchip"
            report.setattrs(
                checks_total=count["total"],
                checks_fail=count[current_app.config["RC_FAILED"]],
                checks_skip=count[current_app.config["RC_SKIPPED"]],
                checks_okay=count[current_app.config["RC_OKAY"]])

            report.hr_size = report.get_hr_size()

        return render_template('cases/search.html', form=form, casenum=case, report_list=report_list)
    # There was an error with the form submission
    elif request.method == "POST":
        flash_errors(form)
    # If no caseid, we return standard form
    return render_template('cases/search.html')


@cases.route('/compare', methods=['POST', 'GET'])
@login_required
def compare():
    """
    Compare multiple reports
    :return: json object: status, msg
    """
    reports = request.get_json()
    if len(reports) < 2:
        return jsonify({"status": "danger",
                        "msg": "We need at least 2 reports to compare"})

    create_event("compare", "report", reports)
    rlist = []
    for r in reports:
        report = db.session.query(Report).filter_by(id=r).first()
        if report is None:
            return jsonify({"status": "danger", "msg": "Report not found"})
        rlist.append(os.path.dirname(report.path))
    outfile = re.match("(/cases/[0-9]+/)", rlist[0]).group(1) + "magui" + str(datetime.datetime.today().strftime('%Y%m%d%H%M%S')) + ".json"
    return magui(outfile, rlist, current_app.config["CITELLUS_PATH"])
