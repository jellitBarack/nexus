from flask import render_template, current_app
from flask_login import login_required
from sqlalchemy.sql import text

from . import trends

from app import db
from app import DefaultObj


@trends.route('/', methods=['GET'])
@login_required
def index():
    """
    Runs multiple queries on the database.
    """

    # Template to get the list of plugins and the percent of getting status %s
    top_by_status = """
    select plugin_id, substring_index(plugin_path, 'citellusclient/plugins/', -1) as plugin_name, count(*) as total, (count(*) / (select count(*)
    from report_checks children where children.plugin_id = parent.plugin_id) * 100) as percent
    from report_checks parent where global_rc = {0} group by plugin_id order by percent desc limit 15;"""

    # Returns the max and avg citellus runtime per report
    durations = get_kv("select max(analyze_duration) as max,avg(analyze_duration) as avg from report_metadata;")
    # Returns count by plugin status (okay, failed, skipped)
    rcs = get_kv("select global_rc as rc,count(*) as count from report_checks group by global_rc;")
    # Returns count by source (magui, citellus)
    source_count = get_kv("select source,count(*) as count from report_metadata group by source;")
    # Total reports
    report_count = get_kv("select count(*) as count from report_metadata;")
    # Report / day for the sparkline
    reports_per_day = get_kv("select date(analyze_time), count(*) as count from report_metadata group by date(analyze_time);")
    # Calculate the average number of checks per reports
    checks_per_report = (rcs.total + report_count.total // 2) // report_count.total
    # Top 15 failed/skipped/okay
    top_failed = get_kv(top_by_status.format(current_app.config["RC_FAILED"]))
    top_skipped = get_kv(top_by_status.format(current_app.config["RC_SKIPPED"]))
    top_okay = get_kv(top_by_status.format(current_app.config["RC_OKAY"]))
    return render_template("trends/dashboard.html", durations=durations, rcs=rcs, source_count=source_count,
                           top_failed=top_failed, report_count=report_count, checks_per_report=checks_per_report,
                           top_skipped=top_skipped, reports_per_day=reports_per_day,
                           top_okay=top_okay)


def get_kv(t):
    """
    Executes a quick query and returns a dict
    :param t: sql query to run
    :return: list of dict of the results
    """
    o = db.engine.execute(text(t))
    ob = Stat(total=0, count=0, list=[])
    list = []
    for r in o:
        d = {}
        for k, v in r.items():
            d[k] = v
            if k == "count":
                ob.total += v
                ob.count += 1
        list.append(d)
    for d in list:
        if "count" in d:
            d["percent"] = float(d["count"]) / float(ob.total) * 100
        ob.list.append(d)
    return ob


class Stat(DefaultObj):
    items = []
    total = 0
    count = 0

    def __init__(self, **kwargs):
        super(Stat, self).__init__(**kwargs)


"""
 select plugin_id,substring_index(plugin_path, 'citellusclient/plugins/', -1),count(*) from report_checks group by plugin_id;
| fd063fa0c6219a14cb4ce9ab8bb4be1a | core/bugzilla/openstack/neutron/1489066.sh                         |      268 |
+--------------------------

select plugin_id,plugin_path,max(execution_time) as max_execution_time, avg(execution_time) as avg_execution_time from report_checks group by plugin_id order by max_execution_time;
| b64620bb79677e1a2fcf3b2f33a9a4b1 | /git/citellus/citellusclient/plugins/core/system/kernel_panic.sh                                                        | 62                 | 1.2873             |
| 3a53906248aa2e4877a344a861d99674 | /git/citellus/citellusclient/plugins/core/openstack/mysql/seqno.sh                                                      | 96                 | 1.0858             |
+------------

select plugin_id, substring_index(plugin_path, 'citellusclient/plugins/', -1), global_rc, count(global_rc) from report_checks group by plugin_id, global_rc

timeline
select analyze_time,execution_time from report_checks left join report_metadata on report_metadata.id = report_checks.report_id where plugin_id = 'fd063fa0c6219a14cb4ce9ab8bb4be1a' order by analyze_time asc;
"""
