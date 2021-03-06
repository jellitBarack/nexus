from collections import defaultdict

from sqlalchemy import func


from app import db
from app.models import CheckResult
from app.models import Check
from app.models import Datahook


def result_string(c):
    """
    Some situations have different result string the reports
    This function tries to guess what's the result string
    :param c: results from the json
    :return: the guessed result string
    """
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
    checks = db.session.query(Check.global_rc, func.count(Check.global_rc)).filter(
        Check.report_id == report_id).group_by(Check.global_rc).all()
    counts = defaultdict(int)
    for c in checks:
        counts["total"] += c[1]
        counts[c[0]] += c[1]
    return counts


def loop_checks(report, current_app):
    """
    Loop through all the checks attached to a report
    and restructure the data for DB insertion
    :param report: a report object with checks attached
    :return: None
    """
    # looping through the plugin results
    # magui is returning a list, while citellus returns a dict
    # converting magui to a dict
    if report.source == "magui":
        md = {}
        for i in report.results:
            md[i["id"]] = i
        report.results = md

    # Defining lists that will be injecting to DB
    checks_to_db = []
    results_to_db = []
    datahooks_to_db = []
    # Loop through the results
    for k, c in report.results.iteritems():
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
                new_results = defaultdict(dict)

                for host in original_results:
                    # When there's 1 failure, all the plugin is failed
                    if original_results[host]["rc"] == current_app.config["RC_FAILED"]:
                        global_rc = current_app.config["RC_FAILED"]

                    # Keeping the count here
                    hostcount[original_results[host]["rc"]] += 1

                    # Restructuring the data
                    new_results = generate_result_list(host, original_results[host], report, new_results)

                # All hosts have skipped?
                if hostcount[current_app.config["RC_SKIPPED"]] == len(original_results):
                    global_rc = current_app.config["RC_SKIPPED"]

                # Completing the object that we will pass to add_check
                element["global_rc"] = global_rc
                element["result"] = new_results
                if report.changed is True:
                    check_obj, result_obj, datahook_obj = add_check(report, element)
                    # We append the object to a list so we can do a mass insert later
                    checks_to_db.append(check_obj)
                    results_to_db.extend(result_obj)
                    datahooks_to_db.extend(datahook_obj)

        else:
            # It's easier to support magui if we convert regular citellus reports with the same
            # Data structure as magui. So let's do this
            new_results = defaultdict(dict)
            new_results = generate_result_list("localhost", original_results, report, new_results)
            c["global_rc"] = current_app.config["RC_OKAY"]
            if new_results["rc"]["localhost"]:
                c["global_rc"] = new_results["rc"]["localhost"]

            c[rs] = new_results
            if report.changed is True:
                check_obj, result_obj, datahook_obj = add_check(report, c)
                checks_to_db.append(check_obj)
                results_to_db.extend(result_obj)
                datahooks_to_db.extend(datahook_obj)

    if report.changed is True:
        db.session.bulk_save_objects(checks_to_db)
        db.session.bulk_save_objects(results_to_db)
        db.session.bulk_save_objects(datahooks_to_db)
        db.session.commit()


def generate_result_list(hostname, items, report, new_results):
    """
    Adds the results to a dict of results
    :param hostname: server hostname
    :param items: dict that contains the results to add
    :param new_results: current results
    return: new_results with new data in it
    """
    new_results["rc"][hostname] = items["rc"]
    new_results["out"][hostname] = items["out"]
    new_results["err"][hostname] = items["err"]
    return new_results


def add_check(report, c):
    """
    Generates Check and CheckResult objects and append them to the list
    to insert them massively in the database later
    :param report: report object
    :param c: check dict from json
    :return: lists of checks and results
    """
    rs = result_string(c)
    # sometimes bugzilla is not defined
    if "bugzilla" not in c:
        c["bugzilla"] = ""
    if "backend" not in c:
        c["backend"] = report.source
    if "long_name" not in c:
        c["long_name"] = c["plugin"]
    if "time" not in c:
        c["time"] = 0
    if "priority" not in c:
        c["priority"] = 0
    result_list = []
    datahook_list = []
    check_obj = Check(report_id=report.id,
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
                      execution_time="{:6.3f}".format(float(c["time"])))

    if "datahook" in c:
        for event in c["datahook"]:
            datahook_list.append(Datahook(check_id=check_obj.id,
                                          event=event,
                                          rc=c["datahook"][event]["rc"],
                                          err=c["datahook"][event]["err"],
                                          out=c["datahook"][event]["out"]))
    for hostname in c[rs]["rc"]:
        result_list.append(CheckResult(check_id=check_obj.id,
                                       hostname=hostname,
                                       result_rc=c[rs]["rc"][hostname],
                                       result_err=c[rs]["err"][hostname],
                                       result_out=c[rs]["out"][hostname]))
    return check_obj, result_list, datahook_list
