from flask import Blueprint

from app import db
import app
import logging
import sys
from collections import defaultdict
from . import views
from app.models import Check
from app.models import CheckResults


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
        # Sometimes the results are stored in result, results or sosreport. Let's guess this
        rs = result_string(c)
        # We need to keep a copy of these results
        original_results = c[rs]
        new_result = {}
        new_result["out"] = {}
        new_result["err"] = {}
        new_result["rc"] = {}
        if c["plugin"] == "citellus-outputs" or c["plugin"] == "metadata-outputs":
            # Restructuring the citellus-outputs
            original_err = c[rs]["err"]

            # We determine a global return code for all the hosts in the report
            # If one is failed, global is failed
            # If all 3 are skipped, global is skipped
            # Otherwize it's okay
            global_rc = current_app.config["RC_OKAY"]
            new_checklist = []
            # We are going to convert the out and err to a string
            # We loop through the citellus plugins
            for element in original_err:
                original_results = element["sosreport"]
                del element["sosreport"]
                # Keeping counts for the skipped
                counts = defaultdict(int)
                for host in original_results:
                    if original_results[host]["rc"] == current_app.config["RC_FAILED"]:
                        global_rc = current_app.config["RC_FAILED"]
                    counts[original_results[host]["rc"]] += 1
                    new_result["rc"][host] = original_results[host]["rc"]
                    new_result["err"][host] = original_results[host]["err"]
                    new_result["out"][host] = original_results[host]["out"]

                if counts[current_app.config["RC_SKIPPED"]] == len(original_results):
                    global_rc = current_app.config["RC_SKIPPED"]
                element["global_rc"] = global_rc
                element["result"] = new_result
                counts["total"] += 1
                counts[global_rc] += 1
                add_check(report_id, element, source)
        
        else:
            # It's easier to support magui if we convert regular citellus reports with the same
            # Data structure as magui. So let's do this
            new_result["rc"]["localhost"] = original_results["rc"]
            new_result["err"]["localhost"] = original_results["err"]
            new_result["out"]["localhost"] = original_results["out"]
            if original_results["rc"]:
                c["global_rc"] = original_results["rc"]
            else:
                 c["global_rc"] = current_app.config["RC_OKAY"]
            c[rs] = new_result
            counts[c["global_rc"]] += 1
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
    if "priority" not in c:
        c["priority"] = 0
    
    check = Check(
                report_id=report_id,
                category=c["category"],
                subcategory=c["subcategory"],
                description=c["description"],
                plugin_path=c["plugin"],
                plugin_id=c["id"],
                backend=c["backend"],
                long_name=c["long_name"],
                bugzilla=c["bugzilla"],
                priority=c["priority"],
                global_rc=c["global_rc"],
                execution_time=round(c["time"],6)
                )
    db.session.merge(check)
    db.session.commit()
    for hostname in c[rs]["rc"]:
        check_result = CheckResults(
                check_id = check.id,
                hostname=hostname,
                result_rc=c[rs]["rc"][hostname],
                result_err=c[rs]["err"][hostname],
                result_out=c[rs]["err"][hostname]
        )
        db.session.merge(check_result)
    db.session.commit()
    return check.id