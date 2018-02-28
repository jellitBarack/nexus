from flask import render_template, current_app, url_for
from flask_login import login_required

from . import home


@home.route('/')
@login_required
def index():
    """
    Render the homepage template on the / route
    """
    return render_template('home/index.html')


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
