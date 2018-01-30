from flask import Blueprint

errors = Blueprint('errors', __name__)

class ReportNotFound(Exception):
    pass

@errors.errorhandler(ReportNotFound)
def reportnotfound(error):
    return render_template("errors/reportnotfound.html"), 404