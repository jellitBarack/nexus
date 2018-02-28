from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

class ReportNotFound(Exception):
    pass


@errors.errorhandler(ReportNotFound)
def reportnotfound(error):
    return render_template("errors/reportnotfound.html"), 404
