from flask import flash, g, redirect, render_template, request, url_for
from flask_httpauth import HTTPTokenAuth
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app.auth import bp
from app import db
from app.auth.forms import LoginForm, UserForm
from app.crud import create_user, read_user_from_token, read_user_from_login
from app.error.errors import api_error
from app.models import User
from app.auth.forms import ResetPasswordRequestForm
from app.auth.email import send_password_reset_email
from app.auth.forms import ResetPasswordForm

token_auth = HTTPTokenAuth('Bearer')


@token_auth.verify_token
def verify_token(token):
    try:
        user = read_user_from_token(token)
        if user is None:
            return False
        g.current_user = user
        return True
    except:
        return False


@token_auth.error_handler
def token_error_handler():
    return api_error(401, 'Invalid authorization')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = read_user_from_login(form)
        if user is None:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        flash('Successfully logged in', 'success')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form, background=True)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = UserForm()
    form.make_create_form()
    if form.validate_on_submit():
        create_user(form)
        flash('Congratulations, you are now a CarWave user!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', title='Register', form=form, background=True)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password', 'info')
        else:
            flash('No account found with that email', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html',
                           title='Reset Password Request', form=form, background=True)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', title="Reset Password", form=form, background=True)