from flask import flash, g, redirect, render_template, request, url_for
from flask_httpauth import HTTPTokenAuth
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.errors.errors import api_error
from app.models import User

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
            password=form.password.data,
        )
        flash("Congratulations, you are now a CarWave user!")
        return redirect(url_for("auth.login"))
    return render_template("register.html", title="Register", form=form)
