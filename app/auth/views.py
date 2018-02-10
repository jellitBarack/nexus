from flask import flash, redirect, render_template, url_for, current_app, request, g, session, jsonify, Response
from flask_login import login_required, login_user, logout_user
from forms import LoginForm, RegistrationForm

import logging
import requests
"""
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import entity
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config
"""


from . import auth
from app import db, google
from app import flash_errors
from app.models import User
import pprint

@auth.route('/login')
def login():
    return google.authorize(callback=url_for('auth.authorized', _external=True))
@auth.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('home.index'))

@auth.route('/login/authorized')
def authorized():
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
    #str = pprint.pformat(dir(google), depth=5)
    #str = pprint.pformat(vars(greq), depth=5)
    #return Response(str, mimetype="text/text")
    #return jsonify(oauth_response)
    return redirect(url_for('home.index'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@auth.route('/password')
@login_required
def password():
    return render_template('layout/not-ready.html')