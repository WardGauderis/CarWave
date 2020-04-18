from datetime import datetime, timedelta

import jwt
from flask import current_app
from json import loads
from geoalchemy2 import Geometry
from sqlalchemy import func
from flask_login import UserMixin
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
#     # TODO: Cascade on delete
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
    # TODO DELETION
    __tablename__ = "passenger_requests"

    ride_id = db.Column(db.Integer, db.ForeignKey("rides.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    status = db.Column(db.Enum("accepted", "pending", "rejected", name="status_enum"), default="pending",
                       nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    last_modified = db.Column(db.DateTime, default=datetime.utcnow())

    ride = db.relationship(
        "Ride", back_populates="requests"
    )
    passenger = db.relationship("User", back_populates="requests")


class User(UserMixin, db.Model):
    # TODO checks in database want alle checks gebeuren nu in de forms
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    firstname = db.Column(db.String(64), nullable=False)
    lastname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128))
    # phone_number = db.Column(db.String(32))
    # created_at = db.Column(db.DateTime, default=datetime.utcnow())

    driver_rides = db.relationship("Ride", back_populates="driver")
    cars = db.relationship("Car", back_populates="owner")

    # passenger_rides = db.relationship("Ride", secondary=ride_links, back_populates="passengers", lazy="dynamic")
    requests = db.relationship(
        "PassengerRequest", back_populates="passenger", lazy="dynamic"
    )

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


class Ride(db.Model):
    # TODO alle checks gebeuren voorlopig in CRUD
    __tablename__ = "rides"

    id = db.Column(db.Integer, primary_key=True)

    driver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    driver = db.relationship("User", back_populates="driver_rides")
    passenger_places = db.Column(db.Integer, nullable=False)

    license_plate = db.Column(db.String(16), db.ForeignKey("cars.license_plate"), nullable=True)
    car = db.relationship("Car", back_populates="rides")

    request_time = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    # departure_time = db.Column(db.DateTime, nullable=True)
    departure_address = db.Column(Geometry("POINT", srid=4326), nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    arrival_address = db.Column(Geometry("POINT", srid=4326), nullable=False)

    requests = db.relationship(
        "PassengerRequest", back_populates="ride", lazy="dynamic"
    )

    def from_form(self, form):
        for key, value in form.generator():
            setattr(self, key, value)
        self.departure_address = f"SRID=4326;POINT({form.from_lat.data} {form.from_lon.data})"
        self.arrival_address = f"SRID=4326;POINT({form.to_lat.data} {form.to_lon.data})"

    def __repr__(self):
        return f"<Ride(id={self.id}, driver={self.driver_id})>"

    def accepted_requests(self):
        return self.requests.filter_by(status="accepted")

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
    # TODO checks in database, on delete
    __tablename__ = "cars"

    license_plate = db.Column(db.String(16), primary_key=True)
    model = db.Column(db.String(128), nullable=False)
    colour = db.Column(db.String(32), nullable=False)
    passenger_places = db.Column(db.Integer, nullable=False)
    build_year = db.Column(db.Integer, nullable=False)
    fuel = db.Column(db.Enum("gasoline", "diesel", "electric", name="fuel_enum"), nullable=False)
    consumption = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship("User", back_populates="cars")
    rides = db.relationship("Ride", back_populates="car")

    def __repr__(self):
        return f"<Car(license_plate={self.license_plate}, passenger_places={self.passenger_places})>"

    def from_form(self, form):
        for key, value in form.generator():
            setattr(self, key, value)
