from flask import flash, redirect, render_template, url_for, current_app, request, abort, jsonify
from flask_login import login_required


import os
import re
import json

import logging

from . import health
from ..helpers import sysstat
from app import db
from app.models import Report
from app.helpers.sosreport import Sosreport
from app.helpers.cpuinfo import Cpuinfo
from app.helpers.meminfo import Meminfo
from app.helpers.blockinfo import Blocks, Blockinfo


@health.route('/<report_id>', methods=['GET'])
@login_required
def display_health(report_id):
    report = Report.query.get(report_id)
    return render_template('health/show.html', report=report,
                           #cpuinfo = cpuinfo.get_all_ratios(),
                           #meminfo = meminfo,
                           #mem_used = meminfo.ratio_mem_used(),
                           #hugepages_used = meminfo.ratio_hugepages_used(),
                           #swap_used = meminfo.ratio_swap_used(),
                           #io = blockinfo.get_list_io(),
                           #blocks = blockinfo.get_list_block(),
                           #inodes = blockinfo.get_list_inode()
                          )


# placeholder route to allow the creation of /health/ url
@health.route('/', methods=['GET'])
@login_required
def index():
    return  render_template('layout/not-ready.html')

@health.route('/<report_id>/get', methods=['POST'])
@login_required
def get_data(report_id):
    report = Report.query.get(report_id)
    if report is None:
        abort(404)
    data = json.loads(request.data)
    logging.debug("Getting data for %s", data)
    if data["graphname"] == "cpu-util-summary":
        cpuinfo = Cpuinfo(report)
        out = cpuinfo.get_all_ratios()
    elif data["graphname"] == "memory-summary":
        meminfo = Meminfo(report)
        memory_used = round(meminfo.ratio_mem_used(), 2)
        swap_used = round(meminfo.ratio_swap_used(), 2)
        hugepages_used = round(meminfo.ratio_hugepages_used(), 2)
        out = {
            "labels": ["Memory", "Swap", "HugePages" ],
            "free": [100 - memory_used, 100 - swap_used, 100 - hugepages_used],
            "used": [ memory_used, swap_used, hugepages_used]
        }
    elif data["graphname"] == "memory-details":
        meminfo = Meminfo(report)
        meminfo.get()
        out = [{"name": "Memory Available", 
                #"value": meminfo.MemAvailable, 
                "value": meminfo.MemFree + meminfo.Buffers + meminfo.Cached + meminfo.Dirty + meminfo.AnonPages + meminfo.Slab + meminfo.VmallocUsed,
#                "children_labels": ["MemFree", "Buffers", "Cached", "Dirty", "AnonPages", "Slab", "VmallocUsed", "Other"],
#                "children_values":[ meminfo.MemFree, meminfo.Buffers, meminfo.Cached, meminfo.Dirty, meminfo.AnonPages, meminfo.Slab, meminfo.VmallocUsed,
#                                   meminfo.MemAvailable - meminfo.MemFree - meminfo.Buffers - meminfo.Cached - meminfo.Dirty - meminfo.AnonPages - meminfo.Slab - meminfo.VmallocUsed]
                 "children": [      
                     {"name": "MemFree", "value": meminfo.MemFree}, 
                     {"name": "Buffers", "value": meminfo.Buffers}, 
                     {"name": "Cached", "value": meminfo.Cached},
                     {"name": "Dirty", "value": meminfo.Dirty},
                     {"name": "AnonPages", "value": meminfo.AnonPages},
                     {"name": "Slab", "value": meminfo.Slab}, 
                     {"name": "VmallocUsed", "value": meminfo.VmallocUsed},
                     #{"name": "Other", "value": meminfo.MemAvailable - meminfo.MemFree - meminfo.Buffers - meminfo.Cached - meminfo.Dirty - meminfo.AnonPages - meminfo.Slab - meminfo.VmallocUsed}

                ]},
                {"name": "HugePages", "value": meminfo.HugePages_Total * meminfo.Hugepagesize,
#                 "children_labels": ["Free", "Reserverd", "Surplus"],
#                 "children_values": [ meminfo.HugePages_Free * meminfo.Hugepagesize, meminfo.HugePages_Rsvd * meminfo.Hugepagesize, meminfo.HugePages_Surp * meminfo.Hugepagesize]
                 "children": [
                     {"name": "Free", "value": meminfo.HugePages_Free * meminfo.Hugepagesize},
                     {"name": "Reserved", "value": meminfo.HugePages_Rsvd * meminfo.Hugepagesize},
                     {"name": "Surplus", "value": meminfo.HugePages_Surp * meminfo.Hugepagesize}
                 ]}]
    return jsonify(out)

@health.route('/<report_id>/cpu', methods=['GET'])
@login_required
def get_cpu(report_id):
    return
