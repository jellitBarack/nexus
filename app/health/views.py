from flask import render_template, abort, jsonify
from flask_login import login_required

import logging

from . import health
from app.models import Report
from app.helpers.cpuinfo import Cpuinfo
from app.helpers.meminfo import Meminfo
from app.helpers.blockinfo import Blocks
from app.helpers.history import create_event


@health.route('/<report_id>', methods=['GET'])
@login_required
def display_health(report_id):
    report = Report.query.get(report_id)
    create_event("health", "report", [report_id])
    return render_template('health/show.html', report=report)
    """
    cpuinfo = cpuinfo.get_all_ratios(),
    meminfo = meminfo,
    mem_used = meminfo.ratio_mem_used(),
    hugepages_used = meminfo.ratio_hugepages_used(),
    swap_used = meminfo.ratio_swap_used(),
    io = blockinfo.get_list_io(),
    blocks = blockinfo.get_list_block(),
    inodes = blockinfo.get_list_inode()
    """


# placeholder route to allow the creation of /health/ url
@health.route('/', methods=['GET'])
@login_required
def index():
    return render_template('layout/not-ready.html')


def get_data(report_id):
    report = Report.query.get(report_id)
    if report is None:
        abort(404)
    return report


@health.route('/<report_id>/cpu_summary', methods=['GET'])
@login_required
def get_cpu_summary(report_id):
    report = get_data(report_id)
    cpuinfo = Cpuinfo(report)
    return jsonify(cpuinfo.get_all_ratios())


@health.route('/<report_id>/mem_summary', methods=['GET'])
@login_required
def get_mem_summary(report_id):
    report = get_data(report_id)
    try:
        meminfo = Meminfo(report)
        memory_used = round(meminfo.ratio_mem_used(), 2)
        swap_used = round(meminfo.ratio_swap_used(), 2)
        hugepages_used = round(meminfo.ratio_hugepages_used(), 2)
        return jsonify({
            "labels": ["Memory", "Swap", "HugePages"],
            "free": [100 - memory_used, 100 - swap_used, 100 - hugepages_used],
            "used": [memory_used, swap_used, hugepages_used]
        })
    except:
        return jsonify({})


@health.route('/<report_id>/mem_details', methods=['GET'])
@login_required
def get_mem_details(report_id):
    report = get_data(report_id)
    meminfo = Meminfo(report)
    meminfo.get()
    try:
        return jsonify([{"name": "Memory Available",
                         "value": meminfo.MemFree + meminfo.Buffers + meminfo.Cached + meminfo.Dirty + meminfo.AnonPages + meminfo.Slab + meminfo.VmallocUsed,
                         "children": [{"name": "MemFree", "value": meminfo.MemFree},
                                      {"name": "Buffers", "value": meminfo.Buffers},
                                      {"name": "Cached", "value": meminfo.Cached},
                                      {"name": "Dirty", "value": meminfo.Dirty},
                                      {"name": "AnonPages", "value": meminfo.AnonPages},
                                      {"name": "Slab", "value": meminfo.Slab},
                                      {"name": "VmallocUsed", "value": meminfo.VmallocUsed}]
                         },
                        {"name": "HugePages", "value": meminfo.HugePages_Total * meminfo.Hugepagesize,
                         "children": [{"name": "Free", "value": meminfo.HugePages_Free * meminfo.Hugepagesize},
                                      {"name": "Reserved", "value": meminfo.HugePages_Rsvd * meminfo.Hugepagesize},
                                      {"name": "Surplus", "value": meminfo.HugePages_Surp * meminfo.Hugepagesize}]
                         }])
    except AttributeError:
        return jsonify({})


@health.route('/<report_id>/blocks_io', methods=['GET'])
@login_required
def get_blocks_io(report_id):
    report = get_data(report_id)
    blocks = Blocks(report)
    blocks.list_io()
    out = []
    for o in blocks.data_table:
        out.append(blocks.data_table[o]["io"].dump())
    return jsonify(out)


@health.route('/<report_id>/blocks_space', methods=['GET'])
@login_required
def get_blocks_space(report_id):
    report = get_data(report_id)
    blocks = Blocks(report)
    blocks.list_block_space()
    out = []
    for o in blocks.data_table:
        try:
            out.append(blocks.data_table[o]["block"].dump())
        except KeyError:
            logging.debug(blocks.data_table[o])
    return jsonify(out)


@health.route('/<report_id>/blocks_inode', methods=['GET'])
@login_required
def get_blocks_inode(report_id):
    report = get_data(report_id)
    blocks = Blocks(report)
    blocks.list_inode_space()
    out = []
    for o in blocks.data_table:
        try:
            out.append(blocks.data_table[o]["inode"].dump())
        except KeyError:
            logging.debug(blocks.data_table[o])
    return jsonify(out)
