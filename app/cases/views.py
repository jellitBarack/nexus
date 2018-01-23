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
from app import flash_errors



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
        """
        for file1 in os.listdir(casepath):
            logging.debug('Dirname1: %s', file1)
            fullpath1 = os.path.join(casepath, file1)
            if os.path.isdir(fullpath1):
                for file2 in os.listdir(fullpath1):
                    logging.debug('Dirname2: %s', file2)
                    fullpath2 = os.path.join(fullpath1, file2)
                    if os.path.isdir(fullpath2):
                        for file3 in os.listdir(fullpath2):
                            logging.debug('Dirname3: %s', file3)
        """
        for root, dirs, files in os.walk(casepath, topdown=True):
            logging.debug("there are %s files in %s", len(files), root)
            if "citellus.json" in files:
                cdata = json.load(open(root+"/citellus.json"))
                counts = defaultdict(int)
                for c in cdata["results"]:
                    counts[c["result"]["rc"]] += 1
                    counts["total"] += 1
                logging.debug(counts)
                sospath = root.split("/")
                citellusList.append({"fullname": root+"/citellus.json", "name": "/".join(sospath[3:]), "icon": "cog", "checks_total": counts["total"], "checks_fail": counts[20], "checks_skip": counts[30], "checks_okay": counts[10], "execution_time": 0})
            if "magui.json" in files:
                maguiList.append(root+"/magui.json")
            if root.count(os.sep) - casepath.count(os.sep) == 2:
                del dirs[:]

        return render_template('cases/search.html', form=form, citellusList=citellusList, maguiList=maguiList, title='Search sosreport in case')
    elif request.method == "POST":
        flash_errors(form)
    return render_template('cases/search.html', form=form, title='Search sosreport in case')
