from flask import flash, redirect, render_template, url_for, current_app, request
from flask_login import login_required, login_user, logout_user
from forms import LoginForm, RegistrationForm

import logging

from . import auth
from app import db
from app import flash_errors
from app.models import User

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add an user to the database through the registration form
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                            username=form.username.data,
                            first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            password=form.password.data)

        # add user to the database
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered! You may now login.', category='success')

        # redirect to the login page
        return redirect(url_for('auth.login'))

    # load registration template
    return render_template('auth/register.html', form=form, title='Register')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle requests to the /login route
    Log an user in through the login form
    """
    form = LoginForm()
    if form.validate_on_submit():
        # check whether user exists in the database and whether
        # the password entered matches the password in the database
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            # log user in
            login_user(user)

            # redirect to the dashboard page after login
            return redirect(url_for('home.index'))

        # when login details are incorrect
        else:
            flash('Invalid username or password.',category='error')
    if request.method == "POST":
        flash_errors(form)

    # load login template
    return render_template('auth/login.html', form=form, title='Login')

@auth.route('/logout')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Log an user out through the logout link
    """
    logout_user()
    flash('You have successfully been logged out.', category='success')

    # redirect to the login page
    return redirect(url_for('auth.login'))
