from flask import Blueprint, g, current_app

health = Blueprint('health', __name__)

from . import views