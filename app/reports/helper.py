import json
import hashlib

from datetime import datetime
from sqlalchemy import or_

from app import db
from app.models import Report


def add_report(report):
    """
    Assemble the information from the json file
    and the metadata we had already.
    It the stores the report in the DB
    :param report: object that was previously scanned
    :return: report object, results list, and if report has changed
    """
    try:
        j = json.load(open(report.fullpath))
    except IOError as e:
        return e.strerror

    report.md5sum = hashlib.md5(open(report.fullpath, 'rb').read()).hexdigest()

    if j["metadata"]["source"] == "magui":
        j["metadata"]["live"] = False
    if "time" not in j["metadata"]:
        j["metadata"]["time"] = 0

    report_db = db.session.query(Report).filter(
        or_(Report.md5sum == report.md5sum, Report.id == report.id)).first()

    report.changed = False
    if report_db is not None and report_db.md5sum != report.md5sum:
        report.changed = True

    report.setattrs(source=j["metadata"]["source"],
                    live=j["metadata"]["live"],
                    analyze_time=datetime.strptime(j["metadata"]["when"], '%Y-%m-%dT%H:%M:%S.%f'),
                    analyze_duration=round(j["metadata"]["time"], 3))

    if report_db is None or report.changed is True:
        report.get_report_size()
        report.get_machine_id()
        report.get_machine_name()
        report.get_collect_time()
        # add report to the database
        if report.changed is True:
            db.session.merge(report)
        else:
            db.session.add(report)

        db.session.commit()
        report.changed = True
    elif report_db is not None and report.changed is False:
        report.size = report_db.size
        report.name = report_db.name
        report.collect_time = report_db.collect_time
        report.machine_id = report.machine_id

    report.results = j["results"]
    return None
