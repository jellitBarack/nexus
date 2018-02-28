from flask import Blueprint

pyinfo = Blueprint('pyinfo', __name__)

from . import views
