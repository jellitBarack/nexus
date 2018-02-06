from flask import flash, redirect, render_template, url_for, current_app, request, g, session, jsonify
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
    logging.debug(dir(greq.data))

    logging.debug(dir(me.data))
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
    return jsonify({"me": me.data, "greq": greq.data})

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@auth.route('/password')
@login_required
def password():
    return render_template('layout/not-ready.html')


"""
SAML Implementation
#https://stackoverflow.com/questions/27932899/saml-2-0-service-provider-in-python
#https://gist.github.com/jpf/67076180b9766f54c430
@auth.route("/saml/sso/<idp_name>", methods=['POST'])
def idp_initiated(idp_name):
    saml_client = saml_client_for(idp_name)
    authn_response = saml_client.parse_authn_request_response(
        request.form['SAMLResponse'],
        entity.BINDING_HTTP_POST)
    authn_response.get_identity()
    user_info = authn_response.get_subject()
    username = user_info.text

    # "JIT provisioning"
    if username not in user_store:
        user_store[username] = {
            'first_name': authn_response.ava['FirstName'][0],
            'last_name': authn_response.ava['LastName'][0],
            }
    user = User(username)
    login_user(user)
    # TODO: If it exists, redirect to request.form['RelayState']
    return redirect(url_for('user'))

@auth.route("/saml/login", methods=['GET', 'POST'])
def sp_initiated():
    idp_name="auth.redhat.com"
    saml_client = saml_client_for(idp_name)
    reqid, info = saml_client.prepare_for_authenticate()

    # NOTE:
    # I realize I _technically_ don't need to set Cache-Control or Pragma here:
    #     http://stackoverflow.com/a/5494469
    # However,
    # Section 3.2.3.2 explicitly of this part of the SAML spec requires it:
    #     http://docs.oasis-open.org/security/saml/v2.0/saml-bindings-2.0-os.pdf
    # We set those headers here as a "belt and suspenders" approach,
    # since enterprise environments don't always coform to RFCs
    redirect_url = None
    for key, value in info['headers']:
        if key is 'Location':
            redirect_url = value
    response = redirect(redirect_url, code=302)
    response.headers['Cache-Control'] = 'no-cache, no-store'
    response.headers['Pragma'] = 'no-cache'
    return response

def saml_client_for(idp_name=None):
    '''
    Given the name of an IdP, return a configuation.
    The configuration is a hash for use by saml2.config.Config
    '''
    acs_url = url_for(
        "auth.idp_initiated",
        idp_name=idp_name,
        _external=True)
    logging.debug(current_app.config)
    rv = requests.get(current_app.config["IDP_SETTINGS"][idp_name]["metadata"]["local"][0])
    # I have to do this because
    # the "inline" metadata type isn't working in PySAML2
    import tempfile
    tmp = tempfile.NamedTemporaryFile()
    f = open(tmp.name, 'w')
    f.write(rv.text)
    f.close()

    settings = {
        'metadata': {
            # 'remote': {
            #     'url': metadata_url_for[idp_name],
            #     'cert': 'asdfasf'
            #     }
            # 'inline': metadata,
            "local": [tmp.name]
            },
        'service': {
            'sp': {
                'endpoints': {
                    'assertion_consumer_service': [
                        (acs_url, BINDING_HTTP_REDIRECT),
                        (acs_url, BINDING_HTTP_POST)
                    ],
                },
                # Don't verify that the incoming requests originate from us via
                # the built-in cache for authn request ids in pysaml2
                'allow_unsolicited': True,
                # Don't sign authn requests
                'authn_requests_signed': False,
                'logout_requests_signed': True,
                'want_assertions_signed': True,
                'want_response_signed': False,
            },
        },
    }
    spConfig = Saml2Config()
    spConfig.load(settings)
    spConfig.allow_unknown_attributes = True
    saml_client = Saml2Client(config=spConfig)
    tmp.close()
    return saml_client
"""