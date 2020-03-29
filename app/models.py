from datetime import datetime, timedelta

import jwt
from flask import current_app
from json import loads
from geoalchemy2 import Geometry
from sqlalchemy import func
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
    # TODO: Cascade on delete
    "car_links",
    db.metadata,
    db.Column("driver_id", db.Integer, db.ForeignKey("drivers.id"), primary_key=True),
    db.Column("car_license_plate", db.String, db.ForeignKey("cars.license_plate"), primary_key=True),
)

ride_links = db.Table(
    # Cascade on delete
    "ride_links",
    db.metadata,
    db.Column("ride_id", db.Integer, db.ForeignKey("rides.id"), primary_key=True),
    db.Column(
        "passenger_id", db.Integer, db.ForeignKey("passengers.id"), primary_key=True
    ),
)


class PassengerRequest(db.Model):
    __tablename__ = "passenger_requests"
    ___tableargs__ = [
        # TODO: CheckConstraint, not present in ride_links
        db.CheckConstraint("ride_id != passenger_id")
    ]

    ride_id = db.Column(db.Integer, db.ForeignKey("rides.id"), primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey("passengers.id"), primary_key=True)
    status = db.Column(db.Enum("pending", "declined", name="status_enum"), default="pending", nullable=False)

    ride = db.relationship(
        "Ride", backref=db.backref("rides", cascade="all, delete-orphan")
    )
    passenger = db.relationship(
        "Passenger", backref=db.backref("passengers", cascade="all, delete-orphan")
    )


# Entities


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128))
    phone_number = db.Column(db.String(32))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

    @staticmethod
    def create(**kwargs):
        try:
            kwargs["password_hash"] = generate_password_hash(kwargs.pop("password"))
        except KeyError:
            raise ValueError("No 'password' keyword argument was supplied")

        try:
            user = User(**kwargs)
            db.session.add(user)
            db.session.commit()
            db.session.add(Driver(id=user.id))
            db.session.commit()
            return user
        except IntegrityError as e:
            db.session.rollback()
            return e

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

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': datetime.utcnow() + timedelta(expires_in)},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except jwt.DecodeError as e:
            return e
        return User.get(id)


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
        "Ride", secondary="passenger_requests", back_populates="requests"
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
        # TODO: driver counts as one so there should be space for at least one more
        # TODO: len(ride.passengers) <= passenger_places
        db.CheckConstraint("passenger_places >= 2"),
        nullable=False,
    )

    # car_license_plate = db.Column(
    #     db.String(16),
    #     db.ForeignKey("cars.license_plate"),
    #     # db.CheckConstraint("passenger_places <= car"),
    #     nullable=True,
    # )
    # car = db.relationship("Car")

    request_time = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=True)
    departure_address = db.Column(Geometry("POINT", srid=4326), nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    arrival_address = db.Column(Geometry("POINT", srid=4326), nullable=False)

    passengers = db.relationship(
        "Passenger",
        secondary=ride_links,
        back_populates="rides"
    )
    requests = db.relationship(
        "Passenger", secondary="passenger_requests", back_populates="requests"
    )

    def __repr__(self):
        return f"<Ride.create(id={self.id}, driver={self.driver_id})>"

    @staticmethod
    def create(**kwargs):
        try:
            dep, arr = kwargs.pop("departure_address"), kwargs.pop("arrival_address")
            kwargs["departure_address"] = f"SRID=4326;POINT({dep[0]} {dep[1]})"
            kwargs["arrival_address"] = f"SRID=4326;POINT({arr[0]} {arr[1]})"
            ride = Ride(**kwargs)
            db.session.add(ride)
            db.session.commit()
            return ride
        except IntegrityError as e:
            db.session.rollback()
            return e

    @staticmethod
    def get(ride_id: int):
        return Ride.query.get(ride_id)

    @property
    def depart_from(self):
        point = loads(db.session.scalar(func.ST_AsGeoJson(self.departure_address)))
        return point["coordinates"]

    @property
    def arrive_at(self):
        point = loads(db.session.scalar(func.ST_AsGeoJson(self.arrival_address)))
        return point["coordinates"]


class Car(db.Model):
    __tablename__ = "cars"

    license_plate = db.Column(db.String(16), primary_key=True)
    model = db.Column(db.String(128), nullable=False)
    colour = db.Column(db.String(32), nullable=False)
    # TODO: # of passengers driver counts as one of the passengers
    passenger_places = db.Column(
        db.Integer, db.CheckConstraint("passenger_places >= 2"), nullable=False
    )

    drivers = db.relationship("Driver", secondary=car_links, back_populates="cars")

    def __repr__(self):
        return f"<Car(license_plate={self.license_plate}, passenger_places={self.passenger_places})>"
