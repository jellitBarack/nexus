import re
import os
import json
from datetime import datetime
from datetime import timedelta
from subprocess import Popen, PIPE
global sadfbin
global sysstat_activies
global sysstat_default_days
from ..config import Config as conf
import logging

sadfbin = conf.SYSSTAT_SADF
sysstat_activies = conf.SYSSTAT_ACTIVITIES
sysstat_default_days = conf.SYSSTAT_DEFAULT_DAYS
default_start_date = datetime.now() - timedelta(days=sysstat_default_days)

class sysstat:
    @staticmethod
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
            if data_type is None:
                args.append("-A")
            else:
                if "." in data_type:
                    a, subact = data_type.split(".")
                    thing = sysstat_activies[a][subact]
                else:
                    thing = sysstat_activies[data_type]
                args.extend(thing["switch"].split())
        out = Popen(args, stdout=PIPE, stderr=PIPE)
        return out

    @staticmethod
    def headers(file):
        """
        Parse a sa file and grabs available activities and date
        :param file: path to var/log/sa/saXX
        :return : dict {"date": "datetime.obj", "A_HEADER": "# of instance(s)" }
        """
        headers = {}
        headers_out = sysstat.sadf(file=file, data_type="header")

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
    @staticmethod
    def get_file_date(folder=None, start_date=None, end_date=datetime.now()):
        """
        To go faster, this preloads the header of each sa file. If it doesn't
        match the date range, it's not going to be parsed
        :param folder: var/log/sa/
        :param (start|end)_date: Date range to look for
        :return : array of dict {filenname: "filename", filedate: "date"}
        """
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
                        h = sysstat.headers(root+f)
                        if start_date <= h["date"] + timedelta(days=1) <= end_date:
                            matching_files.append({
                                'filename': root+f,
                                'filedate': h["date"]
                            })
        else:
            raise Exception("Invalid folder: " + folder)
        if len(matching_files) == 0:
            return []

        return sorted(matching_files, key=lambda k: k["filedate"])
    @staticmethod
    def pd_get_stats(stat):
        logging.debug(stat)
    @staticmethod
    def get_stats(file=None, get_metadata=None, activity=None, data_type=None, start_date=None, end_date=datetime.now(), filter_list=None, filter_condition=None):
        """
        This is a dispatcher function to get points/activities/keys
        :param single file: path to a var/log/sa/sa[0-9]+
        :param get_metadata: accepts "keys" or "activities"
        :param activity: activity (cpu, mem, network.net-dev, etc)
        :param data_type: to match config["SYSSTAT_ACTIVITIES"], passed too sadf
        :param (start|end)_date: range of date to look for
        :param filter_list: array of filters ([{"key": "ifrace", "operator": "==", "value": "em1"},...]) 
        :param filter_contition: "and" or "or"
        :return : either keys, activities or filtered items
        """
        #import numpy
        #import pandas as pd
        
        global default_start_date
        if start_date is None:
            start_date = default_start_date
        stats = "".join(sysstat.sadf(file=file, data_type=data_type).stdout)
        jstats = json.loads(stats)
        dated_events = sysstat.get_event_by_date(stats=jstats, start_date=start_date, end_date=end_date)
        #df = pd.DataFrame(dated_events)
        #logging.debug(df)
        #s = df.set_index('date')['a']
        if get_metadata == "keys":
            matching_events = sysstat.get_event_keys(dated_events, activity)
        elif get_metadata == "activities":
            matching_events = sysstat.get_event_activities(dated_events)
        else:
            matching_events = sysstat.transform_stats(stats=dated_events, activity=activity, data_type=data_type, filter_list=filter_list, filter_condition=filter_condition)
        return matching_events

    @staticmethod
    def get_event_time(stats):
        """
        Extracts the timestamp of said event
        :param stats: stat under ["sysstat"]["hosts"][0]["statistics"]
        :return : datetime Object
        """
        timestamp = stats["timestamp"]["date"] + " " + stats["timestamp"]["time"]
        return datetime.strptime(stats["timestamp"]["date"] + " " + stats["timestamp"]["time"], '%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def get_event_by_date(stats, start_date=None, end_date=datetime.now()):
        """
        Find the events that match a start_date and an end_date
        :param stats: a stats dict built from the json of sadf
        :param start_date: Timestamp must be greater than this date
        :param end_date: Timestamp must be smaller than this date
        """
        global default_start_date
        if start_date is None:
            start_date = default_start_date
        matching_events = []
        for s in stats["sysstat"]["hosts"][0]["statistics"]:
            event_date = sysstat.get_event_time(s)
            if start_date <= event_date <= end_date:
                matching_events.append(s)
        #logging.debug("Matching Events: %s", matching_events)
        return matching_events

    @staticmethod
    def get_event_activities(stats):
        """
        Gets a list of activities in a range of stats
        We just need to sample the first event
        :param stats
        :return : list of activities
        """
        keylist = []
        del stats[-1]["timestamp"]
        for k in stats[-1]:
            logging.debug("Key: %s", k)
            if "is-parent" in sysstat_activies[k] and sysstat_activies[k]["is-parent"] == "true":
                for sk in stats[-1][k]:
                    keylist.append(k + "." + sk)
            else:
                keylist.append(k)
        return sorted(keylist)
    
    @staticmethod
    def get_event_keys(stats, activity):
        keylist = []
        if "." in activity:
            a, subact = activity.split(".")
            thing = stats[-1][a][subact]
        else:
            thing = stats[-1][activity]
        if not isinstance(thing, list):
            thing = [thing]
        return sorted(thing[-1].keys())

    @staticmethod
    def transform_stats(stats=None, activity=None, data_type="all", filter_list=None, filter_condition=None):
        """
        Transform filtered stats into something that C3 can ingest
        :param stats: Stats
        :param activity: activity (cpu, mem, network.net-dev, etc)
        :param data_type: to match config["SYSSTAT_ACTIVITIES"], passed too sadf
        :param filter_list: array of filters ([{"key": "ifrace", "operator": "==", "value": "em1"},...]) 
        :param filter_contition: "and" or "or"
        :return : C3 timeseries: [{"timestamp": "2018-01-04 00:00:01", }]
         """
        matching_events = []
        for s in stats:
            if "." in activity:
                a, subact = activity.split(".")
                thing = s[a][subact]
            else:
                thing = s[activity]

            if not isinstance(thing, list):
                thing = [thing]
            for t in thing:
                if filter_list:
                    fr = sysstat.filter_event(t, filter_list, filter_condition)
                else:
                    fr = True
                if fr is True:
                    matching_events.append({
                        "timestamp": s["timestamp"],
                        "stats": t
                    })

        return sorted(matching_events, key=lambda k: k["timestamp"])

    @staticmethod
    def filter_event(event, filter_list, filter_condition="and"):
        """
        Determine if an event matches a filter with eval 
        (yes, this is ugly, let me know if we can do this otherwize)
        :param event: event object from transform_stats
        :param filter_list: list of filter dict. ie: [{"key": "iface","op": "==","value": "em1"}]
        :param condition: "and" or "or"
        :return: true of false
        """
        if isinstance(event, list):
            thing = event[0]
        else:
            thing = event
        if len(filter_list) > 0:
            evalstr = ""
            for f in filter_list:
                if f["key"] not in thing:
                    raise Exception("Filter key %s is not in event %s", f["key"], thing)
                if f["operator"] not in ["==", "!=", ">", ">=", "<", "<=", "is", "is not"]:
                    raise Exception("Filter operator invalid " + f["operator"])
                evalstr += ' ' + filter_condition + ' "' + str(thing[f["key"]]) + '" ' + f["operator"] + ' '
                if isinstance(f["value"], int) or isinstance(f["value"], float):
                    evalstr += str(f["value"])
                else:
                    evalstr += '"' + f["value"] + '"'
            evalstr = re.sub("^ " + filter_condition + " ", "", evalstr)
            outeval = eval(evalstr)
        return outeval

"""
Test zone, please ignore
"""

class Statset(object):
    def __init__(self, timestamp, activity, key, value, label):
        self.timetamp = timestamp
        self.activity = activity
        self.keys = keys
        self.label = label

    def match_filter(self, filter_list, filter_condition):
        if len(filter_list) > 0:
            evalstr = ""
            for f in filter_list:
                if f["key"] not in self.things:
                    raise Exception("Filter key %s is not in event %s", f["key"], self)
                if f["operator"] not in ["==", "!=", ">", ">=", "<", "<=", "is", "is not"]:
                    raise Exception("Filter operator invalid " + f["operator"])
                evalstr += ' ' + filter_condition + ' "' + str(thing[f["key"]]) + '" ' + f["operator"] + ' '
                if isinstance(f["value"], int) or isinstance(f["value"], float):
                    evalstr += str(f["value"])
                else:
                    evalstr += '"' + f["value"] + '"'
            logging.debug(evalstr)
            evalstr = re.sub("^ " + filter_condition + " ", "", evalstr)
            outeval = eval(evalstr)
        return outeval