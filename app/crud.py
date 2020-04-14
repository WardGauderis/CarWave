from app.models import User, db, current_app
from flask import abort
from jwt import decode, DecodeError


def create_user(form) -> User:
    try:
        user = User(form)
        db.session.add(user)
        db.session.commit()
        return user
    except:
        db.session.rollback()
        abort(400, 'Invalid user creation')


def read_user_from_login(form) -> User:
    try:
        user = User.query.filter_by(username=form.username.data).one_or_none()
        if user is not None and user.check_password(form.password.data):
            return user
        return None
    except:
        abort(400, 'Invalid user login')


def read_user_from_token(token) -> User:
    try:
        data = decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
        return User.query.get(data["id"])
    except DecodeError:
        return None
    except:
        abort(400, 'Invalid user token')


def update_user(user: User, form):
    try:
        user.__init__(form)
        db.session.commit()
    except:
        db.session.rollback()
        abort(400, 'Invalid user update')


def delete_user(user: User):
    try:
        db.session.delete(user)
        db.session.commit()
    except:
        db.session.rollback()
        abort(400, 'Invalid user deletion')
