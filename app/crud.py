from app.models import User, db, current_app, Ride
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


def create_drive(form, user: User) -> Ride:
    try:
        drive = Ride(form)
        drive.driver_id = user.id
        db.session.add(drive)
        db.session.commit()
        return drive
    except:
        db.session.rollback()
        abort(400, 'Invalid drive creation')


def read_drive_from_driver(driver: User) -> Ride:
    try:
        return driver.driver_rides
    except:
        abort(400, 'Invalid drive read from user')


def read_drive_from_id(id: int) -> Ride:
    try:
        return Ride.query.get(id)
    except:
        abort(400, 'Invalid drive read from user')


def read_all_drives(limit: int = None) -> list:
    try:
        if limit is None:
            return Ride.query.all()
        return Ride.query.limit(limit).all()
    except:
        abort(400, 'Invalid drive read')


def update_drive(drive: Ride, form):
    try:
        drive.__init__(form)
        db.session.commit()
    except:
        db.session.rollback()
        abort(400, 'Invalid drive update')


def delete_drive(drive: Ride):
    try:
        db.session.delete(drive)
        db.session.commit()
    except:
        abort(400, 'Invalid drive deletion')
