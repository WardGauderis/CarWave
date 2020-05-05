from datetime import datetime, timedelta
from hashlib import md5
from json import loads
from typing import List

import jwt
import requests
from flask import current_app
from flask_login import UserMixin
from geoalchemy2 import Geometry
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from app import db, login


def to_point(coords):
    return f"SRID=4326;POINT({' '.join(coords)})"


class PassengerRequest(db.Model):
    __tablename__ = "passenger_requests"

    ride_id = db.Column(db.Integer, db.ForeignKey("rides.id", ondelete="CASCADE"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    status = db.Column(
        db.Enum("accepted", "pending", "rejected", name="status_enum"),
        default="pending",
        nullable=False,
    )
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
    address = db.Column(db.String(128), nullable=True)

    driver_rides = db.relationship(
        "Ride", back_populates="driver", cascade="all, delete, delete-orphan", lazy="dynamic"
    )
    cars = db.relationship("Car", back_populates="owner", cascade="all, delete, delete-orphan")

    requests = db.relationship(
        "PassengerRequest",
        back_populates="passenger",
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
    )

    written_reviews = db.relationship('Review', back_populates='author', foreign_keys='Review.from_id')
    received_reviews = db.relationship('Review', back_populates='subject', foreign_keys='Review.to_id')

    def avatar(self, size):
        if self.email:
            mail = self.email
        else:
            mail = self.username
        digest = md5(mail.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(digest, size)

    def from_form(self, form):
        for key, value in form.generator():
            setattr(self, key, value)
        if not form.update:
            self.set_password(form.password.data)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

    def accepted_passenger_requests(self):
        return self.requests.filter_by(status="accepted")

    def future_or_past_passenger_requests(self, future_or_past: str = '') -> List[PassengerRequest]:
        query = self.requests.join(Ride)
        if future_or_past == 'future':
            query = query.filter(Ride.arrival_time > datetime.utcnow())
        elif future_or_past == 'past':
            query = query.filter(Ride.arrival_time <= datetime.utcnow())
        return query.all()

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
            {"reset_password": self.id, "exp": datetime.utcnow() + timedelta(expires_in), },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])[
                "reset_password"
            ]
        except jwt.DecodeError as e:
            return e
        return User.query.get(id)

    def get_tags(self, as_driver: bool) -> List[str]:
        return db.engine.execute(
            'select tag.title from tag join review r on tag.review_id = r.id '
            f'where r.to_id = {self.id} and r.as_driver = {as_driver} '
            'group by tag.title order by count(tag.title) desc limit 10;').fetchall()

    def get_rating(self) -> int:
        res = db.session.query(func.avg(Review.rating).label('average')).filter(Review.subject == self).one_or_none()
        if res.average is None:
            return res.average
        return round(res.average)

    def may_review_driver(self, user) -> bool:
        return db.engine.execute('select case when exists(select ride_id from rides join passenger_requests pr on '
                                 'rides.id = pr.ride_id and pr.status = \'accepted\' '
                                 f'where rides.arrival_time > now() and {self.id} != {user.id} '
                                 f'and (pr.user_id = {self.id} and rides.driver_id = {user.id})'
                                 ') then 1 else 0 end;').fetchone()[0]

    def may_review_passenger(self, user) -> bool:
        return db.engine.execute('select case when exists (select r.id from rides r '
                                 'join passenger_requests pr1 on r.id = pr1.ride_id and pr1.status = \'accepted\' '
                                 'join passenger_requests pr2 on r.id = pr2.ride_id and pr2.status = \'accepted\' '
                                 f'where r.arrival_time > now() and {self.id} != {user.id} '
                                 f'and pr1.user_id = {self.id} and pr2.user_id = {user.id} '
                                 f'or r.driver_id = {self.id} and pr1.user_id = {user.id}) '
                                 'then 1 else 0 end;').fetchone()[0]


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Ride(db.Model):
    __tablename__ = "rides"

    id = db.Column(db.Integer, primary_key=True)

    driver_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    driver = db.relationship("User", back_populates="driver_rides", single_parent=True)
    passenger_places = db.Column(db.Integer, nullable=False)

    license_plate = db.Column(
        db.String(16), db.ForeignKey("cars.license_plate", ondelete="SET NULL"), nullable=True,
    )
    car = db.relationship("Car", back_populates="rides")

    request_time = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=True)
    departure_address = db.Column(Geometry("POINT", srid=4326), nullable=False)
    departure_id = db.Column(db.String(32), nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    arrival_address = db.Column(Geometry("POINT", srid=4326), nullable=False)
    arrival_id = db.Column(db.String(32), nullable=False)

    requests = db.relationship(
        "PassengerRequest",
        back_populates="ride",
        lazy="dynamic",
        cascade="all, delete, delete-orphan",
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
            if data["osm_type"] == "way":
                return "W" + str(data["osm_id"])
            if data["osm_type"] == "relation":
                return "R" + str(data["osm_id"])
            if data["osm_type"] == "node":
                return "N" + str(data["osm_id"])
            return data["osm_type"] + data["osm_id"]

        if not form.arrival_id.data:
            self.arrival_id = location_to_id(form.to_lon.data, form.to_lat.data)
        if not form.departure_id.data:
            self.departure_id = location_to_id(form.from_lon.data, form.from_lat.data)

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
    consumption = db.Column(db.Float, nullable=False)  # liter per 100 kilometer

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = db.relationship("User", back_populates="cars", single_parent=True)
    rides = db.relationship("Ride", back_populates="car", lazy='dynamic')

    def __repr__(self):
        return (
            f"<Car(license_plate={self.license_plate}, passenger_places={self.passenger_places})>"
        )

    def from_form(self, form):
        for key, value in form.generator():
            setattr(self, key, value)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    to_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    as_driver = db.Column(db.Boolean, nullable=False)
    review = db.Column(db.String(1024), nullable=False)
    rating = db.Column(db.Integer, nullable=False, )
    last_modified = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    __table_args__ = (db.UniqueConstraint('from_id', 'to_id', 'as_driver', name='one_review'),
                      db.CheckConstraint('from_id != to_id', name='review_others'),
                      db.CheckConstraint('rating <= 10 and rating >= 0', name='rating_check'))

    tags = db.relationship('Tag', back_populates='review')
    author = db.relationship('User', back_populates='written_reviews', foreign_keys=[from_id])
    subject = db.relationship('User', back_populates='received_reviews', foreign_keys=[to_id])


class Tag(db.Model):
    review_id = db.Column(db.Integer, db.ForeignKey('review.id', ondelete='CASCADE'), primary_key=True)
    title = db.Column(db.String(64), primary_key=True)

    review = db.relationship('Review', back_populates='tags')
