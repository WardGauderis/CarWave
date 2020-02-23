from app import db
from datetime import datetime

"""
File with the database models described using SQLAlchemy
"""

# TODO: address & rides relationships

# Relationships


belongs_to = db.Table(
    "belongs_to",
    db.metadata,
    db.Column("driver_id", db.Integer, db.ForeignKey("drivers.id")),
    db.Column("car_id", db.Integer, db.ForeignKey("cars.id")),
)


# Entities


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"))  # m2m
    phone_number = db.Column(db.String)

    def __repr__(self):
        # return f"<User(id={self.id}, name={self.first_name + ' ' + self.last_name})>"
        pass


class Driver(User):
    """
    Driver is a User
    """

    __tablename__ = "drivers"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    rating = db.column(db.Integer, nullable=False)
    cars = db.relationship("Car", secondary=belongs_to, back_populates="cars")

    def __repr__(self):
        pass


class Passenger(User):
    """
    Passenger is a User
    """

    __tablename__ = "passengers"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    rating = db.column(db.Integer, nullable=False)

    def __repr__(self):
        pass


class Ride(db.Model):
    __tablename__ = "rides"

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(  # one2m
        db.Integer, db.ForeignKey("drivers.id"), nullable=False
    )
    passenger_id = db.Column(  # m2m
        db.Integer, db.ForeignKey("passengers.id"), nullable=False
    )
    request_time = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime)

    def __repr__(self):
        pass


class Address(db.Model):
    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True)
    # FIXME: unique. index?
    address = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        pass


class Car(db.Model):
    __tablename__ = "cars"

    license_plate = db.column(db.String, primary_key=True)
    model = db.column(db.String, nullable=True)
    colour = db.column(db.String, nullable=True)
    num_passengers = db.column(db.Integer, nullable=False)
    owners = db.relationship(
        "Driver", secondary=belongs_to, back_populates="drivers"
    )

    def __repr__(self):
        pass
