from flask import Blueprint

from collections import defaultdict

checks = Blueprint('checks', __name__)

from app import db
from . import views
from app.models import Check

# Sometimes it's results, some other time it's result, 
# depending if called from magui or citellus
def result_string(c):
    if "result" not in c:
        result_string = "results"
    else:
        result_string = "result"
    return result_string

def loop_checks(report_id, results, source):
    # looping through the plugin results
    counts = defaultdict(int)
    
    for c in results:
        rs = result_string(c)
        # Counting plugins
        counts[c[rs]["rc"]] += 1
        counts["total"] += 1
        add_check(report_id, c, source)

    return counts

def add_check(report_id, c, source):
    rs = result_string(c)
    # sometimes bugzilla is not defined
    if "bugzilla" not in c:
        c["bugzilla"] = ""
    if "backend" not in c:
        c["backend"] = source
    if "long_name" not in c:
        c["long_name"] = c["plugin"]
    
    if c["plugin"] is "citellus-outputs":
        counts = loop_checks(report_id, c[result_string]["err"], source)

    check = Check(report_id=report_id,
                category=c["category"],
                subcategory=c["subcategory"],
                description=c["description"],
                plugin_path=c["plugin"],
                plugin_id=c["id"],
                backend=c["backend"],
                long_name=c["long_name"],
                bugzilla=c["bugzilla"],
                result_rc=c[rs]["rc"],
                result_err=c[rs]["err"],
                result_out=c[rs]["out"],
                time=c["time"])

    # add check to the database
    db.session.merge(check)
    db.session.commit()
    return check.id