from flask import Blueprint

health = Blueprint('health', __name__)

from . import views
