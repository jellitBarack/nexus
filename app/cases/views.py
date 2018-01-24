from flask import flash, redirect, render_template, url_for, current_app, request
from flask_login import login_required, login_user, logout_user
from os.path import dirname as up
from collections import defaultdict

import os
import fnmatch
import app
import logging
import json

from . import cases
from forms import CaseSearchForm
from app.models import Report
from app.models import Check
from app import flash_errors
from app import db



@cases.route('/', methods=['GET', 'POST'])
def search():
    """
    Handle requests for cases
    """
    form = CaseSearchForm()
    if form.validate_on_submit():
        casepath = "/cases/" + form.casenum.data
        logging.debug('Case Path: %s', casepath)
        citellusList = []
        maguiList = []
        for root, dirs, files in os.walk(casepath, topdown=True):
            logging.debug("there are %s files in %s", len(files), root)
            if "citellus.json" in files:
                cdata = json.load(open(root+"/citellus.json"))

                # Can't use the path from the metadata because
                # the path is used to generate the unique ID
                # And sometimes, the path is simply . 
                report = Report(source=cdata["metadata"]["source"],
                            live=cdata["metadata"]["live"],
                            path="/".join(root.split("/")[-2:]),
                            when=cdata["metadata"]["when"],
                            time=cdata["metadata"]["time"])

                # add report to the database
                db.session.merge(report)
                db.session.commit()
                
                # looping through the plugin results
                counts = defaultdict(int)
                for c in cdata["results"]:
                    # Counting plugins
                    counts[c["result"]["rc"]] += 1
                    counts["total"] += 1
                    if "bugzilla" not in c:
                        c["bugzilla"] = ""
                    check = Check(report_id=report.id,
                                category=c["category"],
                                subcategory=c["subcategory"],
                                description=c["description"],
                                plugin_path=c["plugin"],
                                plugin_id=c["id"],
                                backend=c["backend"],
                                long_name=c["long_name"],
                                bugzilla=c["bugzilla"],
                                result_rc=c["result"]["rc"],
                                result_err=c["result"]["err"],
                                result_out=c["result"]["out"],
                                time=c["time"],
                                )
                # add check to the database
                db.session.merge(check)
                db.session.commit()

                # add report to the web interface
                citellusList.append({"fullname": root+"/citellus.json", 
                                "name": "/".join(root.split("/")[-2:]), 
                                "icon": "cog", 
                                "checks_total": counts["total"], 
                                "checks_fail": counts[20], 
                                "checks_skip": counts[30], 
                                "checks_okay": counts[10], 
                                "execution_time": 0})

            if "magui.json" in files:
                maguiList.append(root+"/magui.json")
            if root.count(os.sep) - casepath.count(os.sep) == 2:
                del dirs[:]

        return render_template('cases/search.html', form=form, citellusList=citellusList, maguiList=maguiList, title='Search sosreport in case')
    elif request.method == "POST":
        flash_errors(form)
    return render_template('cases/search.html', form=form, title='Search sosreport in case')
