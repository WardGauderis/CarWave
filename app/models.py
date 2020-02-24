from datetime import datetime

from app import db

"""
File with the database models described using SQLAlchemy
"""

# Relationships


car_links = db.Table(
    "car_links",
    db.metadata,
    db.Column("driver_id", db.Integer, db.ForeignKey("drivers.id")),
    db.Column(
        "car_license_plate", db.String, db.ForeignKey("cars.license_plate")
    ),
)

ride_links = db.Table(
    "ride_links",
    db.metadata,
    db.Column("ride_id", db.Integer, db.ForeignKey("rides.id")),
    db.Column("passenger_id", db.Integer, db.ForeignKey("passengers.id")),
)

# Entities

# FIXME: one2one relationship link to driver & passenger
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"))
    phone_number = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    address = db.relationship("Address")

    def __repr__(self):
        return f"<User(id={self.id})>"


class Driver(User):
    """
    Driver is a User
    """

    __tablename__ = "drivers"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    rating = db.Column(
        db.Numeric(precision=1, scale=1),
        db.CheckConstraint("0.0 <= rating AND rating <= 5.0"),
        nullable=False,
    )

    rides = db.relationship("Ride", back_populates="driver")
    cars = db.relationship("Car", secondary=car_links, back_populates="drivers")

    def __repr__(self):
        return f"<Driver(id={self.id}, rating={self.rating})>"


class Passenger(User):
    """
    Passenger is a User
    """

    __tablename__ = "passengers"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    rating = db.Column(
        db.Numeric(precision=1, scale=1),
        db.CheckConstraint("0.0 <= rating AND rating <= 5.0"),
        nullable=False,
    )

    rides = db.relationship(
        "Ride", secondary=ride_links, back_populates="passengers"
    )

    def __repr__(self):
        return f"<Passenger(id={self.id}, rating={self.rating})>"


class Ride(db.Model):
    __tablename__ = "rides"

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(
        db.Integer, db.ForeignKey("drivers.id"), nullable=False
    )
    request_time = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime)

    driver = db.relationship("Driver", back_populates="rides")
    passengers = db.relationship(
        "Passenger", secondary=ride_links, back_populates="rides"
    )

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
        "Driver", secondary=car_links, back_populates="cars"
    )

    def __repr__(self):
        return f"<Car(license_plate={self.license_plate}, num_passengers={self.num_passengers})>"
