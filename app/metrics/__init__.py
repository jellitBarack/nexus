from flask import Blueprint

metrics = Blueprint('metrics', __name__)

from . import views
