from flask import Blueprint

history = Blueprint('history', __name__)

from . import views
