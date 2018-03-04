import re
import os
import subprocess
from flask import jsonify
from app.models import Report
from app.helpers import sysstat


def find_reports(path, case, report_file_names):
    """
    Look for reports in path
    :param path: Path of extracted sosreport
    :param case: case id
    :return reports: list of Reports
    """
    report_list = []
    combinedregex = re.compile("(" + ")|(".join(report_file_names) + ")")
    for root, dirs, files in os.walk(path, topdown=True):
        matched = filter(combinedregex.match, files)
        if len(matched) == 0:
            continue
        for f in matched:
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


def magui(outfile, reports, citellus_path):
    """
    Runs magui (compare tool) on reports
    :param outfile: json output file generated by magui
    :param reports: list of report ids
    :return: json object with execution status
    """
    args = ["python", citellus_path + "/magui.py"]
    args.extend(["--loglevel", "DEBUG", "-o", outfile])
    args.extend(reports)
    command = " ".join(args)
    try:
        subprocess.check_output([command], shell=True)
    except subprocess.CalledProcessError:
        return jsonify({"status": "danger",
                        "msg": "An error occurred while executing command."})
    return jsonify({"status": "success",
                    "msg": "Succesfully generated compare report"})
