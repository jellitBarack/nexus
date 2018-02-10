from flask import flash, redirect, render_template, url_for, current_app, request, g, session, jsonify, Response
from flask_login import login_required, login_user, logout_user

import logging
import requests

from . import auth
from app import db, google
from app import flash_errors
from app.models import User

@auth.route('/login')
def login():
    return google.authorize(callback=url_for('auth.authorized', _external=True))
@auth.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('home.index'))

@auth.route('/login/authorized')
def authorized():
    next_url = request.args.get('next') or url_for('home.index')
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    greq = google.get("http_request")
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
    return jsonify(request.args)
    #return redirect(next_url)

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@auth.route('/password')
@login_required
def password():
    return render_template('layout/not-ready.html')