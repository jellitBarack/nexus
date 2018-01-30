from flask import Blueprint, g, current_app

metrics = Blueprint('metrics', __name__)

from . import views
from subprocess import Popen, PIPE
import re
import os
import json
from datetime import datetime
from datetime import timedelta
import app
import logging
global sadfbin
global sysstat_activies
global sysstat_default_days

@metrics.record
def setup(state):
    global sadfbin
    global sysstat_activies
    global sysstat_default_days
    global default_start_date
    current_app = state.app
    sadfbin = current_app.config["SYSSTAT_SADF"]
    sysstat_activies = current_app.config["SYSSTAT_ACTIVITIES"]
    sysstat_default_days = current_app.config["SYSSTAT_DEFAULT_DAYS"]
    default_start_date = datetime.now() - timedelta(days=sysstat_default_days)


def sadf(file=None, data_type=None):
    if file is None:
        raise Exception("No file specified")

    if os.path.isfile(file) is False:
        raise Exception("File %s is invalid", file)

    if os.access(file, os.R_OK) is False:
        raise Exception("File %s is not readable", file)

    args = [sadfbin]
    if data_type is "header":
        args.extend(["-H",file])
    else:
        args.extend(["-j",file,"--"])
        args.extend(sysstat_activies[data_type]["switch"].split())
    out = Popen(args, stdout=PIPE, stderr=PIPE)
    return out

def headers(file):
    headers = {}
    headers_out = sadf(file=file, data_type="header")

    for line in headers_out.stdout:
        rd = re.match(r'.*[\s]+([0-9]{1,2})\/([0-9]{1,2})\/([0-9]{2,4})[\s]+.*', line)
        if rd:
            year = rd.group(3)
            if len(year) == 2:
                year = "20" + str(year)
            date = year + "-" + rd.group(1) + "-" + rd.group(2) + " 0:00:00"
            headers["date"] = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        rh = re.match(r'^[0-9]+: A_([^\s]+)[\s]+\(x([0-9]+)\)', line)
        if rh:
            headers[rh.group(1)] = rh.group(2)

    return headers

def get_stats(file=None, data_type=None, start_date=None, end_date=datetime.now(), filter_list=None, filter_condition=None):
    global default_start_date
    if start_date is None:
        start_date = default_start_date
    stats = "".join(sadf(file=file, data_type=data_type).stdout)
    jstats = json.loads(stats)
    matching_events = transform_stats(stats=jstats, **kwargs)
    return matching_events

def transform_stats(stats=None, start_date=None, end_date=datetime.now(), filter_list=None, filter_condition=None):
    global default_start_date
    if start_date is None:
        start_date = default_start_date
    matching_events = []
    for s in stats["sysstat"]["hosts"][0]["statistics"]:
        timestamp = s["timestamp"]["date"] + " " + s["timestamp"]["time"]
        event_date = datetime.strptime(s["timestamp"]["date"] + " " + s["timestamp"]["time"], '%Y-%m-%d %H:%M:%S')
        if start_date <= event_date <= end_date:
            for key in s.keys():
                if key != "timestamp":
                    for k in s[key].keys():
                        for r in s[key][k]:
                            if filter_list is not None:
                                fr = filter_event(r, filter_list, filter_condition)
                            else:
                                fr = True
                            if fr is True:
                                matching_events.append({
                                    "timestamp": event_date,
                                    "stats": r
                                })
    return matching_events

def filter_event(event, filter_list, filter_condition="and"):
    """
    Determine if an event matches a filter with eval 
    (yes, this is ugly, let me know if we can do this otherwize)
    :param event: event object from transform_stats
    :param filter_list: list of filter dict. ie: [{"key": "iface","op": "==","value": "em1"}]
    :param condition: "and" or "or"
    :return: true of false
    """
    if len(filter_list) > 0:
        evalstr = ""
        for f in filter_list:
            if f["key"] not in event:
                raise Exception("Filter key " + f["key"] + " is not in event " + event)
            if f["op"] not in ["==", ">", ">=", "<", "<=", "is", "is not"]:
                raise Exception("Filter operator invalid " + f["op"])
            evalstr += ' ' + filter_condition + ' "' + str(event[f["key"]]) + '" ' + f["op"] + ' '
            if isinstance(f["value"], int) or isinstance(f["value"], float):
                evalstr += str(f["value"])
            else:
                evalstr += '"' + f["value"] + '"'
        evalstr = re.sub("^ " + filter_condition + " ", "", evalstr)
        outeval = eval(evalstr)
    return outeval

def get_file_date(folder=None, start_date=None, end_date=datetime.now()):
    global default_start_date
    if start_date is None:
        start_date = default_start_date
    matching_files = []
    folder = re.sub("/$", "", folder)
    folder += "/"
    if os.path.isdir(folder):
        for root, dirs, files in os.walk(folder, topdown=True):
            for f in files:
                if re.match(r'^sa[0-9]+$', f):
                    h = headers(root+f)
                    logging.debug(h)
                    if start_date <= h["date"]  <= end_date:
                        matching_files.append({
                            'filename': root+f,
                            'filedate': h["date"]
                        })
    else:
        raise Exception("Invalid folder: " + folder)
    if len(matching_files) == 0:
        raise Exception("No matching files found")
        
    return sorted(matching_files, key=lambda k: k["filedate"])


"""
Execution example
def main():
   # out = get_stats(file=testfile, data_type="NET_DEV")
   testdate = datetime.now() - timedelta(days=30)
   files = get_file_date(folder="/cases/02005200/sosreport-20180105-164506/controller0/var/log/sa", start_date = testdate)
   filter_list = [{
       "key": "iface",
       "op": "==",
       "value": "em1"
    },
    {
        "key": "txdrop",
        "op": ">=",
        "value": 0
    }
   ]
   filter_condition = "and"
   for f in files:
       print f["filename"] + "\n"
       matching_events = get_stats(file=f["filename"], data_type="NET_EDEV", start_date=testdate, filter_list=filter_list, filter_condition=filter_condition)
       print matching_events
"""