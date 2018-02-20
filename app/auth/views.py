from flask import flash, redirect, url_for, current_app, request, g, session, jsonify, Response
from flask_login import login_required, login_user, logout_user

import logging
import requests
import base64

from . import auth
from app import db, google
from app import flash_errors
from app.models import User

@auth.route('/login')
def login():
    if request.referrer is None:
        ref64 = base64.b64encode(url_for('home.index'))
    else:
        ref64 = base64.b64encode(request.referrer)
    return google.authorize(state=ref64, callback=url_for('auth.authorized', _external=True))
@auth.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('home.index'))

@auth.route('/login/authorized')
def authorized(state=None):
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    user = User.query.filter_by(id=me.data["id"]).first()
    if user is None:
        user = User(
                id=me.data["id"],
                email=me.data["email"],
                username=me.data["email"],
                last_name=me.data["family_name"],
                first_name=me.data["given_name"],
        )
        db.session.merge(user)
        db.session.commit()
    login_user(user)
    query_state = request.args.get('state')
    if state is not None:
        url = base64.b64decode(state)
    elif query_state is not None:
        url = base64.b64decode(query_state)
    else:
        url = url_for('home.index')
    return redirect(url)

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')
