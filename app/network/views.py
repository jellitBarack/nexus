from flask import flash, render_template
from flask_login import login_required

from . import network
from app.models import Report
from subprocess import check_output, CalledProcessError
from app.helpers.history import create_event


@network.route('/<report_id>', methods=['GET'])
@login_required
def display_network(report_id):
    report = Report.query.get(report_id)
    plotfile = report.path + "/sos_commands/networking/plotnetcfg"
    plotfilesvg = plotfile + ".svg"
    command = "/usr/bin/dot -Tsvg " + plotfile + " -o " + plotfilesvg
    try:
        check_output([command], shell=True)
    except CalledProcessError as e:
        flash(u"Unable to create networking topology: %s" % (e),
              category="error")
    create_event("network", "report", [report_id])
    return render_template('network/show.html', report=report)


@network.route('/', methods=['GET'])
@login_required
def index():
    return render_template('layout/not-ready.html')
