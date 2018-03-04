from flask import Blueprint

checks = Blueprint('checks', __name__)

from . import views
