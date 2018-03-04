from flask import Blueprint

trends = Blueprint('trends', __name__)

from . import views
