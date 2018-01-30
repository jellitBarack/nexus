from subprocess import Popen, PIPE
import re
import os
import json
from datetime import datetime
from datetime import timedelta


sadfbin = "/git/sysstat-10.1.5/sadf"
#testfile = "/cases/02005200/sosreport-20180105-164506/controller0/var/log/sa/sa01"
testfile = "/cases/02005200/sosreport-20180105-164506/corea-controller0.mtcelab.com/var/log/sa/sa01"
default_start_date = datetime.now() - timedelta(days=1*365)
stat_activity = {
    "INT": { "name": "interupts", "switch": "-I"},
    "CPU": { "name": "CPU Utilization", "switch": "-u"},
    "SWAP": { "name": "Swap Utilization", "switch": "-S"},
    "PAGE": { "name": "paging", "switch": "-B"},
    "IO": { "name": "I/O and transfert rates", "switch": "-b"},
    "DISK": { "name": "Block devices", "switch": "-d" },
    "XDISK": { "name": "Filesystem", "switch": "-F" },
    "MEMORY": { "name": "Memory", "switch": "-R"},
    "MEMORY_UTIL": { "name": "Memory Utilization", "switch": "-r"},
    "HUGE": {"name": "Hugepages", "switch": "-H"},
    "INODES": {"name": "Inodes", "switch": "-v"},
    "SWAPPING": {"name": "Swapping", "switch": "-w"},
    "PCSW": {"name": "Task Creation and switching", "switch": "-w"},
    "QUEUE": { "name": "Queue Length", "switch": "-q"},
    "NET_DEV": { "name": "Network Devices", "switch": "-n DEV"},
    "NET_EDEV": { "name": "Network Devices Errors", "switch": "-n EDEV"},
    "NET_NFS": { "name": "NFS Client", "switch": "-n NFS"},
    "NET_NFSD":{ "name": "NFS Server", "switch": "-n NFSD"},
    "NET_SOCK": { "name": "SOCK IPv4", "switch": "-n SOCK"},
    "NET_IP": { "name": "IPv4 network traffic", "switch": "-n IP"},
    "NET_EIP": { "name": "IPv4 network errors", "switch": "-n EIP"},
    "NET_ICMP": { "name": "ICMP IPv4 network traffic", "switch": "-n ICMP"},
    "NET_EICMP": { "name": "ICMP IPv4 network errors", "switch": "-n EICMP"},
    "NET_TCP": { "name": "TCP network traffic", "switch": "-n TCP"},
    "NET_TCP": { "name": "TCP network errors", "switch": "-n ETCP"},
    "NET_UDP": { "name": "UDP IPv6 network traffic", "switch": "-n UDP"},
    "NET_IP6": { "name": "IPv6 network traffic", "switch": "-n IP6"},
    "NET_EIP6": { "name": "IPv6 network errors", "switch": "-n EIP6"},
    "NET_ICMP6": { "name": "ICMP IPv6 network traffic", "switch": "-n ICMP6"},
    "NET_EICMP6": { "name": "ICMP IPv6 network errors", "switch": "-n EICMP6"},
    "NET_SOCK6": { "name": "SOCK IPv6", "switch": "-n SOCK6"},
    "NET_UDP6": { "name": "UDP IPv6 network traffic", "switch": "-n UDP6"},
    "PwR_CPU": { "name": "CPU Power", "switch": "-m CPU" },
    "PwR_FAN": { "name": "FAN RPM", "switch": "-m FAN" },
    "PwR_FREQ": { "name": "CPU Clock frequency", "switch": "-m FREQ" },
    "PwR_IN": { "name": "Input Power", "switch": "-m IN" },
    "PwR_TEMP": { "name": "Temperature", "switch": "-m TEMP" },
}
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
        args.extend(stat_activity[data_type]["switch"].split())
    out = Popen(args, stdout=PIPE, stderr=PIPE)
    return out

def sadf_headers(file):
    headers = {}
    headers_out = sadf(file=file, data_type="header")

    for line in headers_out.stdout:
        rd = re.match(".*[\s]+(\d{1,2})\/(\d{1,2})\/(\d{4})[\s]+.*", line)
        if rd:
            date = rd.group(3) + "-" + rd.group(1) + "-" + rd.group(2) + " 0:00:00"
            headers["date"] = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        rh = re.match(r'^[0-9]+: A_([^\s]+)[\s]+\(x([0-9]+)\)', line)
        if rh:
            headers[rh.group(1)] = rh.group(2)

    return headers

def sadf_get_stats(file=None, data_type=None, start_date=default_start_date, end_date=datetime.now(), filter_list=None, filter_condition=None):
    stats = "".join(sadf(file=file, data_type=data_type).stdout)
    jstats = json.loads(stats)
    matching_events = sadf_transform_stats(stats=jstats, start_date=start_date, end_date=end_date, filter_list=filter_list, filter_condition=filter_condition)
    return matching_events

def sadf_transform_stats(stats=None, start_date=default_start_date, end_date=datetime.now(), filter_list=None, filter_condition=None):
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
                                fr = sadf_filter_event(r, filter_list, filter_condition)
                            else:
                                fr = True
                            if fr is True:
                                matching_events.append({
                                    "timestamp": event_date,
                                    "stats": r
                                })
    return matching_events

def sadf_filter_event(event, filter_list, filter_condition="and"):
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

def sadf_get_file_date(folder=None, start_date=default_start_date, end_date=datetime.now()):
    matching_files = []
    folder = re.sub("/$", "", folder)
    folder += "/"
    if os.path.isdir(folder):
        for root, dirs, files in os.walk(folder, topdown=True):
            for f in files:
                if re.match(r'^sa[0-9]+$', f):
                    h = sadf_headers(root+f)
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

def main():
   # out = sadf_get_stats(file=testfile, data_type="NET_DEV")
   testdate = datetime.now() - timedelta(days=30)
   files = sadf_get_file_date(folder="/cases/02005200/sosreport-20180105-164506/controller0/var/log/sa", start_date = testdate)
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
       matching_events = sadf_get_stats(file=f["filename"], data_type="NET_EDEV", start_date=testdate, filter_list=filter_list, filter_condition=filter_condition)
       print matching_events

if __name__ == "__main__":
    main()

"""
{"sysstat": {
        "sysdata-version": 2.15,
        "hosts": [
                {
                        "nodename": "corea-controller0.mtcelab.com",
                        "sysname": "Linux",
                        "release": "5.10.0-514.26.2.el7.x86_64",
                        "machine": "x86_64",
                        "number-of-cpus": 48,
                        "file-date": "2017-12-31",
                        "statistics": [
                                {
                                        "timestamp": {"date": "2018-01-01", "time": "00:10:01", "utc": 1, "interval": 600},
                                        "network": {
                                                "net-dev": [
                                                        {"iface": "vlan40", "rxpck": 0.47, "txpck": 0.10, "rxkB": 0.02, "txkB": 0.01, "rxcmp": 0.00, "txcmp": 0.00, "rxmcst": 0.00},
                                                        {"iface": "vlan71", "rxpck": 17.71, "txpck": 17.63, "rxkB": 2.48, "txkB": 2.72, "rxcmp": 0.00, "txcmp": 0.00, "rxmcst": 0.00},
                                                        {"iface": "bond1", "rxpck": 4740.22, "txpck": 3525.22, "rxkB": 2150.32, "txkB": 1450.39, "rxcmp": 0.00, "txcmp": 0.00, "rxmcst": 957.31},
                                                        {"iface": "ovs-system", "rxpck": 0.00, "txpck": 0.00, "rxkB": 0.00, "txkB": 0.00, "rxcmp": 0.00, "txcmp": 0.00, "rxmcst": 0.00},
                                                        {"iface": "p3p1", "rxpck": 1.00, "txpck": 0.00, "rxkB": 0.12, "txkB": 0.00, "rxcmp": 0.00, "txcmp": 0.00, "rxmcst": 0.99},
                                                        {"iface": "br-int", "rxpck": 0.00, "txpck": 0.00, "rxkB": 0.00, "txkB": 0.00, "rxcmp": 0.00, "txcmp": 0.00, "rxmcst": 0.00},
"""