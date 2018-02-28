# third-party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from os import getenv

db = SQLAlchemy()

# https://stackoverflow.com/questions/11536764/how-to-fix-attempted-relative-import-in-non-package-even-with-init-py
if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

# Local import
from app import config
from app import create_app

config_name = getenv('FLASK_CONFIG')
app = create_app(config_name, True)
# from app.models import User


manager = Manager(app)
manager.add_command('db', MigrateCommand)

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
