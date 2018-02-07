from flask import flash, redirect, render_template, url_for, current_app, request, abort, jsonify
from flask_login import login_required


import os
import re
import json

import logging

from . import health
from ..helpers import sysstat
from app import db
from app.models import Report

@health.route('/<report_id>', methods=['GET'])
@login_required
def display_health(report_id):
    report = Report.query.get(report_id)

    return render_template('health/show.html', report=report)


# placeholder route to allow the creation of /metrics/ url
@health.route('/', methods=['GET'])
@login_required
def index():
    return  render_template('layout/not-ready.html')
