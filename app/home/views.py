from flask import render_template, current_app, url_for
from flask_login import login_required

from datetime import datetime, timedelta

from app import db
from app.models import Report
from . import home


@home.route('/')
@login_required
def index():
    """
    Render the homepage template on the / route
    """
    q = db.session.query(Report)
    q = q.filter(Report.collect_time.between(datetime.now(), datetime.now() - timedelta(hours=24)))
    q = q.order_by(Report.collect_time.desc()).limit(15)

    return render_template('home/index.html', last_reports=q)


@home.route('/dashboard')
@login_required
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    return render_template('home/dashboard.html', title="Dashboard")


@home.route("/site-map")
def site_map():
    links = []
    for rule in current_app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            links.append((url_for(rule.endpoint, **(rule.defaults or {})), rule.endpoint))
    # links is now a list of url, endpoint tuples
    return render_template('home/sitemap.html', out=links)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)
