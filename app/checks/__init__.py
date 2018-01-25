from flask import Blueprint

from app import db
import app
import logging
import sys
from collections import defaultdict
from . import views
from app.models import Check


checks = Blueprint('checks', __name__)
checks.config = {}
global current_app

@checks.record
def setup(state):
    # Tried to load citellusclient but it doesn't work, 
    #  ImportError: No module named citellusclient
    global citellus
    global current_app
    current_app = state.app
    sys.path.insert(0, state.app.config["CITELLUS_PATH"])
    #from citellusclient import shell as citellus
    

# Sometimes it's results, some other time it's result, 
# depending if called from magui or citellus
def result_string(c):
    if "results" in c:
        result_string = "results"
    elif "result" in c:
        result_string = "result"
    elif "sosreport" in c:
        result_string = "sosreport"
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
    if "time" not in c:
        c["time"] = 0
    
    if c["plugin"] == "citellus-outputs" or c["plugin"] == "metadata-outputs":
        # Restructuring the citellus-outputs
        original_err = c[rs]["err"]
        # We determine a global return code for all the hosts in the report
        # If one is failed, global is failed
        # If all 3 are skipped, global is skipped
        # Otherwize it's okay
        global_rc = current_app.config["RC_OKAY"]

        # We are going to convert the out and err to a string
        global_out = ""
        global_err = ""
        new_checklist = []
        # We loop through the citellus plugins
        for element in original_err:
            new_result = {}
            original_results = element["sosreport"]
            del element["sosreport"]
            
            # Keeping counts for the skipped
            counts = defaultdict(int)
            for host in original_results:

                if original_results[host]["rc"] == current_app.config["RC_FAILED"]:
                    global_rc = current_app.config["RC_FAILED"]
                global_out += "# " + host + ":\n" + original_results[host]["out"]
                global_err += "# " + host + ":\n" + original_results[host]["err"]
                counts[original_results[host]["rc"]] += 1

            if counts[current_app.config["RC_SKIPPED"]] == len(original_results):
                global_rc = current_app.config["RC_SKIPPED"]

            new_result["rc"] = global_rc
            new_result["out"] = global_out
            new_result["err"] = global_err
            element["result"] = new_result
            new_checklist.append(element)

        loop_checks(report_id, new_checklist, source)
        c[rs]["err"] = ""
        c[rs]["out"] = ""

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
                execution_time=round(c["time"],6)
                )

    # add check to the database
    db.session.merge(check)
    db.session.commit()
    return check.id