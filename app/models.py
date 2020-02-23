from app import db
from datetime import datetime

"""
File with the database models described using SQLAlchemy
"""

# Relationships

belongs_to = db.Table(
    db.Column(
        "driver_id", db.Integer, db.ForeignKey("drivers.id"), primary_key=True
    ),
    db.Column("car_id", db.Integer, db.ForeignKey("cars.id"), primary_key=True),
)


# Entities


class User(db.Model):
    """
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # TODO: FK
    address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"))
    phone_number = db.Column(db.String)

    @staticmethod
    def get_user(id: int):
        return None


class Driver(User):
    """
    Driver is a User
    """

    __tablename__ = "drivers"
    rating = db.column(db.Integer, nullable=False)


class Passenger(User):
    """
    Passenger is a User
    """

    __tablename__ = "passengers"
    rating = db.column(db.Integer, nullable=False)


class Ride(db.Model):
    """
    """

    __tablename__ = "rides"
    id = db.Column(db.Integer, primary_key=True)
    # driver_id = db.relationship() one2m
    # passenger_id = db.relationship() m2m
    request_time = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime)


class Address(db.Model):
    """
    """

    __tablename__ = "addresses"
    id = db.Column(db.Integer, primary_key=True)


class Car(db.Model):
    """
    """

    __tablename__ = "cars"
    license_plate = db.column(db.String, primary_key=True)
    model = db.column(db.String, nullable=True)
    colour = db.column(db.String, nullable=True)
    num_passengers = db.column(db.Integer, nullable=False)
    belongs_to = db.relationship(
        "?", # TODO:
        secondary=belongs_to,
        lazy="subquery",
        backref=db.backref("pages", lazy=True),
    )
