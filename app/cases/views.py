from flask import flash, redirect, render_template, url_for, current_app, request
from flask_login import login_required, login_user, logout_user

from . import auth
from forms import LoginForm, RegistrationForm
from .. import db
from ..models import User
from app import flash_errors


@auth.route('/', methods=['GET', 'POST'])
def case():
    """
    Handle requests for cases
    """
    form = CaseForm
    if form.validate_on_submit():
        # redirect to the login page
        return redirect(url_for('auth.login'))

    # load registration template
    return render_template('cases/register.html', form=form, title='Register')
