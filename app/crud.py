from app.models import User, db, current_app, Ride, PassengerRequest, Car
from flask import abort
from jwt import decode, DecodeError
from datetime import datetime


def create_user(form) -> User:
    try:
        user = User()
        user.from_form(form)
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


def read_user_from_id(id) -> User:
    try:
        return User.query.get(id)
    except:
        abort(400, 'Invalid user id')


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
        user.from_form(form)
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
        drive = Ride()
        drive.from_form(form)
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


def search_drives() -> list:  # TODO
    pass


def update_drive(drive: Ride, form):
    try:
        drive.from_form(form)
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


def create_passenger_request(passenger: User, drive: Ride) -> PassengerRequest:
    if passenger == drive.driver:
        abort(400, 'Driver cannot be a passenger in his own ride')
    elif read_passenger_request(passenger, drive):
        abort(400, 'User has already created a passenger request for this ride')
    try:
        request = PassengerRequest()
        request.ride_id = drive.id
        request.user_id = passenger.id
        db.session.add(request)
        db.session.commit()
        return request
    except:
        db.session.rollback()
        abort(400, 'Invalid passenger request')


def read_passenger_request(passenger: User, drive: Ride) -> PassengerRequest:
    try:
        return PassengerRequest.query.get((drive.id, passenger.id))
    except:
        abort(400, 'Invalid passenger request read')


def update_passenger_request(request: PassengerRequest, action: str) -> PassengerRequest:
    if request.status != "pending":
        abort(400, "This request is not pending")
    if action == "accept":
        if not request.ride.has_place_left():
            abort(400, "This request cannot be accepted because there are no passenger places left")
        request.status = "accepted"
    elif action == "reject":
        request.status = "rejected"
    else:
        abort(400, 'Invalid passenger request update')
    try:
        request.last_modified = datetime.utcnow()
        db.session.commit()
        return request
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(400, 'Invalid passenger request update')


def delete_passenger_request(request: PassengerRequest):
    try:
        db.session.delete(request)
        db.session.commit()
    except:
        abort(400, 'Invalid passenger request deletion')


def create_car(form, user: User) -> Car:
    try:
        car = Car()
        car.from_form(form)
        car.user_id = user.id
        db.session.add(car)
        db.session.commit()
        return car
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(400, 'Invalid car creation')


def read_car_from_plate(plate: str) -> Car:
    try:
        return Car.query.get(plate)
    except:
        abort(400, 'Invalid car plate')


def update_car(car: Car, form) -> Car:
    try:
        car.from_form(form)
        db.session.commit()
    except:
        db.session.rollback()
        abort(400, 'Invalid car update')


def delete_car(car: Car):
    try:
        db.session.delete(car)
        db.session.commit()
    except:
        abort(400, 'Invalid Car deletion')
