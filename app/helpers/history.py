from flask_login import current_user

from app import db

from ..models import History


def create_event(action, item_type, item_ids, user_id=None):
    """
    Creates an event in the history table
    :param action: Action can be show/compare/yank/etc
    :param item_type: case/report
    :param item_ids: casenum or report_id
    """
    if user_id is None:
        user_id = current_user.get_id()
    history_list = []
    for i in item_ids:
        History.query.filter(History.item_type == item_type, History.item_id == i, History.user_id == user_id, History.action == action).delete()
        h = History(item_type=item_type,
                    action=action,
                    item_id=i,
                    user_id=user_id)
        history_list.append(h)

    db.session.bulk_save_objects(history_list)
    db.session.commit()
