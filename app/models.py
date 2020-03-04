from datetime import datetime, timedelta

import jwt
from flask import current_app
from flask_login import UserMixin
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login

"""
File with the database models described using SQLAlchemy

TODO:
    - Add more ease of use functions for fulfilling API requests and the like
    - Get rides as a passenger or driver for a user
    - Handle passenger requests for a certain driver
    - How to delete a passenger request?
    - Serialise models to JSON for the API requests?
"""

# The secondary tables for the many-to-many relationships

car_links = db.Table(
    "car_links",
    db.metadata,
    db.Column("driver_id", db.Integer, db.ForeignKey("drivers.id")),
    db.Column("car_license_plate", db.String, db.ForeignKey("cars.license_plate")),
)

ride_links = db.Table(
    "ride_links",
    db.metadata,
    db.Column("ride_id", db.Integer, db.ForeignKey("rides.id")),
    db.Column("passenger_id", db.Integer, db.ForeignKey("passengers.id")),
)

# TODO: add request status else we have no way to track declined requests
# enum {PENDING, DECLINED}, ACCEPTED -> added to ride.passengers so no need
passenger_requests = db.Table(
    "passenger_requests",
    db.metadata,
    db.Column("ride_id", db.Integer, db.ForeignKey("rides.id")),
    db.Column("passenger_id", db.Integer, db.ForeignKey("passengers.id")),
)


# Entities


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email_adress = db.Column(db.String(128))
    address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"))
    phone_number = db.Column(db.String(32))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    address = db.relationship("Address")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

    @staticmethod
    def create_user(**kwargs) -> int:
        try:
            # TODO: Reject passwords shorter than a specified length. probably in the form
            kwargs["password_hash"] = generate_password_hash(kwargs.pop("password"))
        except KeyError:
            raise ValueError("No 'password' keyword argument was supplied")

        try:
            user = User(**kwargs)
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            # TODO: log error
            return None

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def from_username(username: str):
        return User.query.filter_by(username=username).one_or_none()

    @staticmethod
    def from_token(token):
        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            return User.query.get(data["id"])
        except jwt.DecodeError:
            return None

    def get_token(self):
        return jwt.encode(
            {"id": self.id, "exp": datetime.utcnow() + timedelta(minutes=30)},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Driver(db.Model):
    """
    Driver is a User
    """

    __tablename__ = "drivers"

    id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True,
    )
    rating = db.Column(
        db.Numeric(precision=2, scale=1),
        db.CheckConstraint("0.0 <= rating AND rating <= 5.0"),
        nullable=True,
    )
    num_ratings = db.Column(db.Integer, default=0, nullable=False)

    user = db.relationship(
        "User", backref=db.backref("driver", uselist=False, passive_deletes=True),
    )
    rides = db.relationship("Ride", back_populates="driver")
    cars = db.relationship("Car", secondary=car_links, back_populates="drivers")

    def __repr__(self):
        return f"<Driver(id={self.id}, rating={self.rating})>"


class Passenger(db.Model):
    """
    Passenger is a User
    """

    __tablename__ = "passengers"

    id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True,
    )
    rating = db.Column(
        db.Numeric(precision=2, scale=1),
        db.CheckConstraint("0.0 <= rating AND rating <= 5.0"),
        default=None,
        nullable=True,
    )
    num_ratings = db.Column(db.Integer, default=0, nullable=False)

    user = db.relationship(
        "User", backref=db.backref("passenger", uselist=False, passive_deletes=True),
    )
    rides = db.relationship("Ride", secondary=ride_links, back_populates="passengers")
    requests = db.relationship(
        "Ride", secondary=passenger_requests, back_populates="requests"
    )

    def __repr__(self):
        return f"<Passenger(id={self.id}, rating={self.rating})>"

    def to_json(self):
        return {"id": self.id, "username": self.user.username}


class Ride(db.Model):
    __tablename__ = "rides"

    id = db.Column(db.Integer, primary_key=True)

    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"), nullable=False)
    driver = db.relationship("Driver", back_populates="rides")
    passenger_places = db.Column(
        db.Integer,
        # TODO: river counts as one so there should be space for at least one more
        # TODO: len(ride.passengers) <= passenger_places
        db.CheckConstraint("passenger_places >= 2"),
        nullable=False,
    )
    # TODO
    # Addable at a later date, but must check car's # of passenger places is
    # greater or equal to the ride's # of passengers
    car_license_plate = db.Column(
        db.String(16),
        db.ForeignKey("cars.license_plate"),
        # db.CheckConstraint("passenger_places <= car"),
        nullable=True,
    )
    car = db.relationship("Car")

    request_time = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    # departure_time = db.Column(db.DateTime, nullable=False)
    # departure_address_id = db.Column(
    #     db.Integer, db.ForeignKey("addresses.id"), nullable=False
    # )
    # departure_address = db.relationship("Address")
    arrival_time = db.Column(db.DateTime, nullable=False)
    # arrival_address_id = db.Column(
    #     db.Integer, db.ForeignKey("addresses.id"), nullable=False
    # )
    # arrival_address = db.relationship("Address")

    passengers = db.relationship(
        "Passenger",
        secondary=ride_links,
        back_populates="rides"
        # FIXME: constraint, len(passengers) < car.num_passengers
    )
    requests = db.relationship(
        "Passenger", secondary=passenger_requests, back_populates="requests"
    )

    # FIXME(Hayaan): Not needed so long as car is a nullable field (API spec).
    # def __init__(self, **kwargs):
    #     try:
    #         driver = Driver.query.get(kwargs["driver_id"])
    #         car = Car.query.get(kwargs["car_license_plate"])
    #     except KeyError:
    #         raise ValueError("Invalid driver_id or car_license_plate args")
    #
    #     if car not in driver.cars:
    #         raise ValueError("The driver cannot use a car they do not own for a ride")
    #
    #     super(Ride, self).__init__(**kwargs)

    def __repr__(self):
        return f"<Ride(id={self.id}, driver={self.driver_id})>"

    @staticmethod
    def create_ride(**kwargs):
        try:
            ride = Ride(**kwargs)
            db.session.add(ride)
            db.session.commit()
            return ride
        except IntegrityError:
            db.session.rollback()
            # TODO: log error
            return None

    @staticmethod
    def get_ride(ride_id: int):
        return Ride.query.get(ride_id)

    # FIXME: should be replaceable with a CheckConstraint
    def add_car(self, car) -> bool:
        if self.passenger_places < car.passenger_places:
            return False
        self.car = car
        db.session.commit()
        return True


class Address(db.Model):
    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(256), unique=True, index=True, nullable=False)

    def __repr__(self):
        return f"<Address(id={self.id}, address={self.address}>"


class Car(db.Model):
    __tablename__ = "cars"

    license_plate = db.Column(db.String(16), primary_key=True)
    model = db.Column(db.String(128), nullable=False)
    # Enum?
    colour = db.Column(db.String(32), nullable=False)
    # TODO: # of passengers driver counts as one of the passengers
    passenger_places = db.Column(
        db.Integer, db.CheckConstraint("passenger_places >= 2"), nullable=False
    )

    drivers = db.relationship("Driver", secondary=car_links, back_populates="cars")

    def __repr__(self):
        return f"<Car(license_plate={self.license_plate}, passenger_places={self.passenger_places})>"
