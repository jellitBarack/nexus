
from flask import render_template
from flask_login import login_required, current_user

from . import history

from app import db
from app.models import Report
from app.models import History


@history.route('/', methods=['GET'])
@login_required
def history_list():
    user_id = current_user.get_id()
    q = db.session.query(History)
    q = q.filter(History.user_id == user_id).order_by(History.time.desc()).all()
    history_list = []
    for h in q:
        h.get_link()
        if h.item_type == "report":
            r = db.session.query(Report).filter(Report.id == h.item_id).first()
            h.report_name = r.name
            h.report_date = r.collect_time
        history_list.append(h)

    return render_template("history/list.html", history_list=history_list)
