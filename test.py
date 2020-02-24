# TODO: remove

import os
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
db = SQLAlchemy(app)


"""
File with the database models described using SQLAlchemy
"""

car_links = db.Table(
    "car_links",
    db.metadata,
    db.Column("driver_id", db.Integer, db.ForeignKey("drivers.id")),
    db.Column(
        "car_license_plate", db.String, db.ForeignKey("cars.license_plate")
    ),
)

# Entities


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"))  # m2one
    phone_number = db.Column(db.String)

    def __repr__(self):
        return f"<User(id={self.id})>"


class Driver(User):
    """
    Driver is a User
    """

    __tablename__ = "drivers"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    # FIXME: numeric, [0.0, 5.0]
    rating = db.Column(db.Integer, nullable=False)
    cars = db.relationship("Car", secondary=car_links, back_populates="cars")

    def __repr__(self):
        return f"<Driver(id={self.id}, rating={self.rating})>"


class Passenger(User):
    """
    Passenger is a User
    """

    __tablename__ = "passengers"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    # FIXME: numeric, [0.0, 5.0]
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Passenger(id={self.id}, rating={self.rating})>"


class Ride(db.Model):
    __tablename__ = "rides"

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(  # TODO: many to one
        db.Integer, db.ForeignKey("drivers.id"), nullable=False
    )
    # passsengers?
    passenger_id = db.Column(db.Integer, db.ForeignKey("passengers.id"))
    request_time = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime)

    passenger = db.relationship("Passenger", backref="passengers")

    def __repr__(self):
        return f"<Ride(id={self.id})>"


class Address(db.Model):
    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Address(id={self.id}, address={self.address}>"


class Car(db.Model):
    __tablename__ = "cars"

    license_plate = db.Column(db.String, primary_key=True)
    model = db.Column(db.String, nullable=False)
    colour = db.Column(db.String, nullable=False)
    num_passengers = db.Column(db.Integer, nullable=False)
    drivers = db.relationship(
        "Driver", secondary=car_links, back_populates="drivers"
    )

    def __repr__(self):
        return f"<Car(license_plate={self.license_plate}, num_passengers={self.num_passengers})>"


db.create_all()
