from flask import flash, g, redirect, render_template, request, url_for
from flask_httpauth import HTTPTokenAuth
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Message
from werkzeug.urls import url_parse

from app.auth import bp
from app import mail
from app import db
from app.auth.forms import LoginForm, RegistrationForm
from app.errors.errors import api_error
from app.models import User
from app.auth.forms import ResetPasswordRequestForm
from app.auth.email import send_password_reset_email
from app.auth.forms import ResetPasswordForm
from app.auth.forms import EditProfileForm

token_auth = HTTPTokenAuth("Bearer")



@token_auth.verify_token
def verify_token(token):
    user = User.from_token(token)
    if user is None:
        return False
    g.current_user = user
    return True


@token_auth.error_handler
def token_error_handler():
    return api_error(401, "Invalid authorization")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("login.html", title="Login", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        # TODO: restrict password length
        User.create_user(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data,
        )
        flash("Congratulations, you are now a CarWave user!")
        return redirect(url_for("auth.login"))
    return render_template("register.html", title="Register", form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password')
        else:
            flash('No account found with that email')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


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
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('profile.html',
                           user=user,
                           posts=posts)

@bp.route('/user/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit(username):
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        # current_user.email = form.email
        # current_user.phone_number = form.phone_number
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('auth.user', username=username))
    else:
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        # form.email = current_user.email
        # form.phone_number = current_user.phone_number
    return render_template('edit_profile.html', form=form)