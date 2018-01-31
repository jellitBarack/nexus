from flask import Blueprint, g, current_app

metrics = Blueprint('metrics', __name__)

from . import views
