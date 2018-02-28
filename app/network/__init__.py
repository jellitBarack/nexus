from flask import Blueprint, g, current_app

network = Blueprint('network', __name__)

from . import views
