# third-party imports
from flask import Flask, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_breadcrumbs import current_breadcrumbs
import datetime
#, sys, os
import logging, sys
import logging.config
import pprint


LOGGING = {
    'version': 1,
    "disable_existing_loggers": True,
    'formatters': { 
        'debug_format': { 
            'format': "%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(funcName)s %(message)s" 
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'debug_format', 
            'stream': 'ext://sys.stderr'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    },
}

# local imports
from config import app_config

# db variable initialization
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name,cli = False):
    logging.config.dictConfig(LOGGING)

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['APPLICATION_ROOT'] = "/citellus"
    from app import models
    db.init_app(app)
    migrate = Migrate(app, db)

    if (cli is False):
        login_manager.init_app(app)
        login_manager.login_message = "You must be logged in to access this page."
        login_manager.login_view = "auth.login"

        from .admin import admin as admin_blueprint
        app.register_blueprint(admin_blueprint, url_prefix='/admin')
        from .cases import cases as cases_blueprint
        app.register_blueprint(cases_blueprint, url_prefix='/cases')
        from .checks import checks as checks_blueprint
        app.register_blueprint(checks_blueprint, url_prefix='/checks')
        from .cases import cases as cases_blueprint
        app.register_blueprint(cases_blueprint, url_prefix='/cases')
        from .history import history as history_blueprint
        app.register_blueprint(history_blueprint, url_prefix='/history')
        from .metrics import metrics as metrics_blueprint
        app.register_blueprint(metrics_blueprint, url_prefix='/metrics')
        from .compare import compare as compare_blueprint
        app.register_blueprint(compare_blueprint, url_prefix='/compare')
        from .reports import reports as reports_blueprint
        app.register_blueprint(reports_blueprint, url_prefix='/reports')
        from .auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint)
        from .home import home as home_blueprint
        app.register_blueprint(home_blueprint)


    return app

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (getattr(form, field).label.text,error), category="error")
