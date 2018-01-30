rom flask import flash, redirect, render_template, url_for, current_app, request, abort
from flask_login import login_required
from sqlalchemy.orm import subqueryload
from collections import defaultdict


import os
import re

import logging

from . import metrics
from app import db
from app.models import Report

@reports.route('/<report_id>', methods=['GET'])
@login_required
def display_metrics(report_id):
    