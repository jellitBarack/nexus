from flask import Blueprint

from app import db
import app
import logging
import sys
from collections import defaultdict
from . import views
from app.models import Check
from app.models import CheckResult
from sqlalchemy import func



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

def count_checks(report_id):
    """
    Returns a count by return_code for plugins
    that were executed in the context of a report
    :param report_id: string with the id of the report
    :return: dict of the count / rc
    """
    logging.debug("Counting checks for report %s", report_id)
    checks = db.session.query(Check.global_rc, func.count(Check.global_rc)).filter(Check.report_id == report_id).group_by(Check.global_rc).all()
    counts = defaultdict(int)
    for c in checks:
        counts["total"] += c[1]
        counts[c[0]] += c[1]
    logging.debug("Count completed")
    return counts


def loop_checks(report, results, report_changed):
    # looping through the plugin results
    # magui is returning a list, while citellus returns a dict
    # converting magui to a dict
    if report.source == "magui":
        md = {}
        for i in results:
            md[i["id"]] = i
        results = md

    # Defining lists that will be injecting to DB
    checks_to_db = []
    results_to_db = []

    # If the report already exists, and it has change, we delete it
    if report_changed is True:
        logging.debug("Report changed, flushing checks")
        Check.query.filter(Check.report_id == report.id).delete()

    # Loop through the results
    for k, c in results.iteritems():
        # Sometimes the results are stored in result, results or sosreport. Let's guess this
        rs = result_string(c)
        # We need to keep a copy of these results
        original_results = c[rs]

        # Here we have a magui report
        if c["plugin"] == "citellus-outputs" or c["plugin"] == "metadata-outputs":
            # Restructuring the citellus-outputs
            original_err = c[rs]["err"]

            # We are going to convert the out and err to a string
            # We loop through the citellus plugins
            for element in original_err:
                # We determine a global return code for all the hosts in the report
                # If one is failed, global is failed
                # If all 3 are skipped, global is skipped
                # Otherwize it's okay
                global_rc = current_app.config["RC_OKAY"]

                # In magui, the results are stored in sosreport object
                original_results = element["sosreport"]
                del element["sosreport"]

                # we need to keep track of the number of hosts
                # so we know when all the hosts skipped it.
                hostcount = defaultdict(int)

                for host in original_results:
                    # When there's 1 failure, all the plugin is failed
                    if original_results[host]["rc"] == current_app.config["RC_FAILED"]:
                        global_rc = current_app.config["RC_FAILED"]

                    # Keeping the count here
                    hostcount[original_results[host]["rc"]] += 1

                    # Restructuring the data
                    new_result = generate_result_list(host, original_results[host], new_result)
                
                # All hosts have skipped?
                if hostcount[current_app.config["RC_SKIPPED"]] == len(original_results):
                    global_rc = current_app.config["RC_SKIPPED"]

                # Completing the object that we will pass to add_check
                element["global_rc"] = global_rc
                element["result"] = new_result
                if report_changed is True:
                   check, results = add_check(report.id, element, report.source)
                   # We append the object to a list so we can do a mass insert later
                   checks_to_db.append(check)
                   results_to_db.extend(results)
        
        else:
            # It's easier to support magui if we convert regular citellus reports with the same
            # Data structure as magui. So let's do this
            new_result = generate_result_list("localhost", original_results)

            if original_results["rc"]:
                c["global_rc"] = original_results["rc"]
            else:
                 c["global_rc"] = current_app.config["RC_OKAY"]

            c[rs] = new_result
            if report_changed is True:
                check, results = add_check(report.id, c, report.source)
                checks_to_db.append(check)
                results_to_db.extend(results)
    
    if report_changed is True:
        db.session.bulk_save_objects(checks_to_db)
        db.session.bulk_save_objects(results_to_db)
        db.session.commit()

def generate_result_list(hostname, items, new_result = None):
    o = defaultdict(dict)
    o["rc"][hostname] = items["rc"]
    o["out"][hostname] = items["out"]
    o["err"][hostname] = items["err"]
    if new_result is not None:
        n = o.copy()
        n.update(new_result)
        return n
    return o
    

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
    results = []
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
        
    for hostname in c[rs]["rc"]:
        results.append(CheckResult(
                check_id = check.id,
                hostname=hostname,
                result_rc=c[rs]["rc"][hostname],
                result_err=c[rs]["err"][hostname],
                result_out=c[rs]["err"][hostname]
        ))
    return check, results
