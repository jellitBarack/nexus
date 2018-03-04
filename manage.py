"""
this script is to initialize the database
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import os
import logging

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
    report_delete = []
    for root, dirs, files in os.walk(path, topdown=True):
        logging.debug("Root %s Dirs %s" % (root, dirs))
        for d in dirs:
            report_list = find_reports(root + "/" + d, d, app.config.get("REPORT_FILE_NAMES"))
            for report in report_list:
                add_report_status = add_report(report)
                logging.debug("Report Path: %s Changed: %s" % (report.fullpath, report.changed))
                if report.changed is True:
                    report_delete.append(report.id)
                    Check.query.filter(Check.report_id==report.id).delete(synchronize_session=False)
                    loop_checks(report, app)
                if add_report_status is not None:
                    logging.error("Error adding report %s: %s" % (report.fullpath, add_report_status))
                 
        if root.count(os.sep) - path.count(os.sep) == 0:
            del dirs[:]

"""
@manager.command
def seed():
    user = User(email="dvd@redhat.com", username="dvd", first_name="David", last_name="Vallee Delisle", is_admin=True,
                password="q1w2e3")
    db.session.add(user)
    user = User(email="iranzo@redhat.com", username="iranzo", first_name="Pablo", last_name="Iranzo Gomez",
                is_admin=True, password="q1w2e3")
    db.session.add(user)
    user = User(email="rcernin@redhat.com", username="rcernin", first_name="Robin", last_name="Cernin", is_admin=True,
                password="q1w2e3")
    db.session.add(user)
    user = User(email="pcaruana@redhat.com", username="pcaruana", first_name="Pablo", last_name="Caruana",
                is_admin=True, password="q1w2e3")
    db.session.add(user)
    user = User(email="mschuppert@redhat.com", username="mschuppert", first_name="Martin", last_name="Schuppert",
                is_admin=True, password="q1w2e3")
    db.session.add(user)
    db.session.commit()
"""

if __name__ == '__main__':
    manager.run()
