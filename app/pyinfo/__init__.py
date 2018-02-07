from flask import Blueprint, g, current_app

pyinfo = Blueprint('pyinfo', __name__)

from . import views
