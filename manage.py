"""
this script is to initialize the database
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import os
import logging
import re

db = SQLAlchemy()

# https://stackoverflow.com/questions/11536764/how-to-fix-attempted-relative-import-in-non-package-even-with-init-py
if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

# Local import
from app.config import app_config
from app import create_app
from app.cases.helper import find_reports
from app.reports.helper import add_report
from app.checks.helper import loop_checks
from app.models import Check

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name, True)


manager = Manager(app)
manager.add_command('db', MigrateCommand)
@manager.command
def crawl():
    path = app.config.get("CASES_PATH")
    for root, dirs, files in os.walk(path, topdown=True):
        logging.debug("Root %s Dirs %s" % (root, dirs))
        for d in dirs:
            if re.match('^0[0-9]{7}$', d) is None:
                continue
            report_list = find_reports(root + "/" + d, d, app.config.get("REPORT_FILE_NAMES"))
            for report in report_list:
                add_report_status = add_report(report)
                if report.changed is True:
                    logging.debug("Report Path: %s ID: %s Changed: %s" % (report.fullpath, report.id, report.changed))
                    Check.query.filter(Check.report_id==report.id).delete(synchronize_session=False)
                    loop_checks(report, app)
                if add_report_status is not None:
                    logging.error("Error adding report %s: %s" % (report.fullpath, add_report_status))

        if root.count(os.sep) - path.count(os.sep) == 0:
            del dirs[:]


if __name__ == '__main__':
    manager.run()
