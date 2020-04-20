from datetime import datetime, timedelta

import jwt
import requests
from flask import current_app
from json import loads
from geoalchemy2 import Geometry
from sqlalchemy import func
from flask_login import UserMixin
from hashlib import md5
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

# car_links = db.Table(
#     "car_links",
#     db.metadata,
#     db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
#     db.Column("car_license_plate", db.String, db.ForeignKey("cars.license_plate"), primary_key=True),
# )


# ride_links = db.Table(
#     "ride_links",
#     db.metadata,
#     db.Column("ride_id", db.Integer, db.ForeignKey("rides.id"), primary_key=True),
#     db.Column(
#         "user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True
#     ),
# )


class PassengerRequest(db.Model):
    __tablename__ = "passenger_requests"

    ride_id = db.Column(db.Integer, db.ForeignKey("rides.id", ondelete='CASCADE'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='CASCADE'), primary_key=True)
    status = db.Column(db.Enum("accepted", "pending", "rejected", name="status_enum"), default="pending",
                       nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    last_modified = db.Column(db.DateTime, default=datetime.utcnow())

    ride = db.relationship("Ride", back_populates="requests", single_parent=True)
    passenger = db.relationship("User", back_populates="requests", single_parent=True)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    firstname = db.Column(db.String(64), nullable=False)
    lastname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128))
    age = db.Column(db.Integer, nullable=True)
    sex = db.Column(db.Enum("male", "female", "non-binary", name="sex_enum"), nullable=True)
    address_id = db.Column(db.String(32), nullable=True)

    driver_rides = db.relationship("Ride", back_populates="driver", cascade="all, delete, delete-orphan")
    cars = db.relationship("Car", back_populates="owner", cascade="all, delete, delete-orphan")

    requests = db.relationship(
        "PassengerRequest", back_populates="passenger", lazy="dynamic", cascade="all, delete, delete-orphan"
    )

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def from_form(self, form):
        for key, value in form.generator():
            setattr(self, key, value)
        if not form.update:
            self.set_password(form.password.data)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

    def passenger_rides(self):
        return self.requests.filter_by(status="accepted").all()

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

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


class Ride(db.Model):
    __tablename__ = "rides"

    id = db.Column(db.Integer, primary_key=True)

    driver_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    driver = db.relationship("User", back_populates="driver_rides", single_parent=True)
    passenger_places = db.Column(db.Integer, nullable=False)

    license_plate = db.Column(db.String(16), db.ForeignKey("cars.license_plate", ondelete='SET NULL'), nullable=True)
    car = db.relationship("Car", back_populates="rides")

    request_time = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=True)
    departure_address = db.Column(Geometry("POINT", srid=4326), nullable=False)
    departure_id = db.Column(db.String(32), nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    arrival_address = db.Column(Geometry("POINT", srid=4326), nullable=False)
    arrival_id = db.Column(db.String(32), nullable=False)

    requests = db.relationship(
        "PassengerRequest", back_populates="ride", lazy="dynamic", cascade="all, delete, delete-orphan"
    )

    def from_form(self, form):
        for key, value in form.generator():
            setattr(self, key, value)
        self.departure_address = f"SRID=4326;POINT({form.from_lat.data} {form.from_lon.data})"
        self.arrival_address = f"SRID=4326;POINT({form.to_lat.data} {form.to_lon.data})"

        def location_to_id(lon, lat):
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {"lat": lat, "lon": lon, "format": "json"}
            r = requests.get(url=url, params=params)
            data = r.json()
            return data.osm_type + data.osm_id

        if not form.arrival_id.data:
            self.arrival_id = location_to_id(form.to_lon.data, form.to_lat.data)
        if not form.departure_id.data:
            self.arrival_id = location_to_id(form.from_lon.data, form.from_lat.data)

    def __repr__(self):
        return f"<Ride(id={self.id}, driver={self.driver_id})>"

    def accepted_requests(self):
        return self.requests.filter_by(status="accepted")

    def pending_requests(self):
        return self.requests.filter_by(status="pending")

    def passenger_places_left(self) -> int:
        return self.passenger_places - self.accepted_requests().count()

    def has_place_left(self) -> bool:
        return self.passenger_places_left() != 0

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
    passenger_places = db.Column(db.Integer, nullable=False)
    build_year = db.Column(db.Integer, nullable=False)
    fuel = db.Column(db.Enum("gasoline", "diesel", "electric", name="fuel_enum"), nullable=False)
    consumption = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    owner = db.relationship("User", back_populates="cars", single_parent=True)
    rides = db.relationship("Ride", back_populates="car")

    def __repr__(self):
        return f"<Car(license_plate={self.license_plate}, passenger_places={self.passenger_places})>"

    def from_form(self, form):
        for key, value in form.generator():
            setattr(self, key, value)

# class Driver(db.Model):
#     """
#     Driver is a User
#     """
#
#     __tablename__ = "drivers"
#
#     id = db.Column(
#         db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True,
#     )
#     rating = db.Column(
#         db.Numeric(precision=2, scale=1),
#         db.CheckConstraint("0.0 <= rating AND rating <= 5.0"),
#         nullable=True,
#     )
#     num_ratings = db.Column(db.Integer, default=0, nullable=False)
#
#     user = db.relationship(
#         "User", backref=db.backref("driver", uselist=False, passive_deletes=True),
#     )
#     rides = db.relationship("Ride", back_populates="driver")
#     cars = db.relationship("Car", secondary=car_links, back_populates="drivers")
#
#     def __repr__(self):
#         return f"<Driver(id={self.id}, rating={self.rating})>"


# class Passenger(db.Model):
#     """
#     Passenger is a User
#     """
#
#     __tablename__ = "passengers"
#
#     id = db.Column(
#         db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True,
#     )
#     rating = db.Column(
#         db.Numeric(precision=2, scale=1),
#         db.CheckConstraint("0.0 <= rating AND rating <= 5.0"),
#         default=None,
#         nullable=True,
#     )
#     num_ratings = db.Column(db.Integer, default=0, nullable=False)
#
#     user = db.relationship(
#         "User", backref=db.backref("passenger", uselist=False, passive_deletes=True),
#     )
#     rides = db.relationship("Ride", secondary=ride_links, back_populates="passengers")
#     requests = db.relationship(
#         "Ride", secondary="passenger_requests", back_populates="requests"
#     )
#
#     def __repr__(self):
#         return f"<Passenger(id={self.id}, rating={self.rating})>"
#
#     def to_json(self):
#         return {"id": self.id, "username": self.user.username}
