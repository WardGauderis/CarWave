from datetime import datetime, timedelta

import jwt
from flask import current_app
from json import loads
from geoalchemy2 import Geometry
from sqlalchemy import func
from flask_login import UserMixin
from sqlalchemy.exc import DatabaseError
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
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("car_license_plate", db.String, db.ForeignKey("cars.license_plate"), primary_key=True),
)

ride_links = db.Table(
    # TODO: Cascade on delete
    # TODO: eliminate redundancy
    "ride_links",
    db.metadata,
    db.Column("ride_id", db.Integer, db.ForeignKey("rides.id"), primary_key=True),
    db.Column(
        "user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True
    ),
)


class PassengerRequest(db.Model):
    __tablename__ = "passenger_requests"

    ride_id = db.Column(db.Integer, db.ForeignKey("rides.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    status = db.Column(db.Enum("accepted", "pending", "declined", name="status_enum"), default="pending",
                       nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    last_modified = db.Column(db.DateTime, default=datetime.utcnow())

    ride = db.relationship(
        "Ride", backref=db.backref("rides", cascade="all, delete-orphan")
    )
    passenger = db.relationship(
        "User", backref=db.backref("users", cascade="all, delete-orphan")
    )

    def update(self, action):
        if action == "accept":
            self.ride.passengers.append(self.passenger)
            self.status = "accepted"
            db.session.add(self.ride)
        elif action == "reject":
            self.status = "rejected"
        else:
            raise ValueError("Undefined action")

        self.last_modified = datetime.utcnow()
        db.session.add(self)

        try:
            db.session.commit()
        except DatabaseError as e:
            return e

        return self


class User(UserMixin, db.Model):
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
    cars = db.relationship("Car", secondary=car_links, back_populates="owners")

    passenger_rides = db.relationship("Ride", secondary=ride_links, back_populates="passengers")
    requests = db.relationship(
        "Ride", secondary="passenger_requests", back_populates="requests"
    )

    def __init__(self, form):
        for key, value in form.generator():
            setattr(self, key, value)
        self.set_password(form.password.data)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

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

    driver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    driver = db.relationship("User", back_populates="driver_rides")
    passenger_places = db.Column(
        db.Integer,
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
        "User",
        secondary=ride_links,
        back_populates="passenger_rides"
    )
    requests = db.relationship(
        "User", secondary="passenger_requests", back_populates="requests"
    )

    def __repr__(self):
        return f"<Ride(id={self.id}, driver={self.driver_id})>"

    @staticmethod
    def create(**kwargs):
        dep, arr = kwargs.pop("departure_address"), kwargs.pop("arrival_address")
        kwargs["departure_address"] = f"SRID=4326;POINT({dep[0]} {dep[1]})"
        kwargs["arrival_address"] = f"SRID=4326;POINT({arr[0]} {arr[1]})"
        ride = Ride(**kwargs)
        db.session.add(ride)

        try:
            db.session.commit()
        except DatabaseError as e:
            db.session.rollback()
            return e

        return ride

    @staticmethod
    def get(ride_id: int):
        return Ride.query.get(ride_id)

    @staticmethod
    def search(limit=5,
               departure=None,
               departure_distance=1000,
               arrival=None,
               arrival_distance=1000,
               arrival_time=None,
               time_delta=timedelta(minutes=30)):
        """
        Departure/arrival = tuple of 2 floats (longitude, latitude)
        TODO: make additional arguments, tuples?
            e.g. arrival=(location, max_distance), arrival_time=(time, delta)
        """
        query = Ride.query
        if departure:
            query = query.filter(
                func.ST_DWithin(Ride.departure_address, departure, departure_distance, True)
            )
        if arrival:
            query = query.filter(
                func.ST_DWithin(Ride.arrival_address, arrival, arrival_distance, True)
            )
        if arrival_time:
            query = query.filter(
                Ride.arrival_time.between(arrival_time - time_delta, arrival_time + time_delta)
            )
        # Sort by distance to departure/arrival?
        # Move the limit out, only really needed for the API AFAIK
        return query.limit(limit).all()

    def post_passenger_request(self, passenger_id):
        request = PassengerRequest(self.id, passenger_id)
        db.session.add(request)
        try:
            db.session.commit()
        except DatabaseError as e:
            db.session.rollback()
            return e
        return request

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

    owners = db.relationship("User", secondary=car_links, back_populates="cars")

    def __repr__(self):
        return f"<Car(license_plate={self.license_plate}, passenger_places={self.passenger_places})>"
