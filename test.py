import os
from datetime import datetime
from random import uniform

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DEBUG_DATABASE_URI")
db = SQLAlchemy(app)

"""
File with the database models described using SQLAlchemy
"""

# The secondary tables for the many-to-many relationships

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


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"))
    phone_number = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    address = db.relationship("Address")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

    @staticmethod
    def create_user(**kwargs) -> int:
        try:
            kwargs["password_hash"] = generate_password_hash(
                kwargs.pop("password")
            )
        except KeyError:
            raise ValueError("No 'password' keyword argument was supplied")

        user = User(**kwargs)
        db.session.add(user)
        db.session.commit()
        return user.id

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)


class Driver(db.Model):
    """
    Driver is a User
    """

    __tablename__ = "drivers"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    rating = db.Column(
        db.Numeric(precision=2, scale=1),
        db.CheckConstraint("0.0 <= rating AND rating <= 5.0"),
        nullable=False,
    )

    user = db.relationship("User")
    rides = db.relationship("Ride", back_populates="driver")
    cars = db.relationship("Car", secondary=car_links, back_populates="drivers")

    def __repr__(self):
        return f"<Driver(id={self.id}, rating={self.rating})>"


class Passenger(db.Model):
    """
    Passenger is a User
    """

    __tablename__ = "passengers"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    rating = db.Column(
        db.Numeric(precision=2, scale=1),
        db.CheckConstraint("0.0 <= rating AND rating <= 5.0"),
        nullable=False,
    )

    user = db.relationship("User")
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
    departure_address_id = db.Column(
        db.Integer, db.ForeignKey("addresses.id"), nullable=False
    )
    arrival_time = db.Column(db.DateTime)
    arrival_address_id = db.Column(
        db.Integer, db.ForeignKey("addresses.id"), nullable=False
    )

    driver = db.relationship("Driver", back_populates="rides")
    passengers = db.relationship(
        "Passenger", secondary=ride_links, back_populates="rides"
    )

    def __repr__(self):
        return f"<Ride(id={self.id}, driver={self.driver_id})>"


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


def main():
    db.reflect()
    db.drop_all()

    db.create_all()

    User.create_user(
        username="dbsrxvqujuce",
        password="$N:K]r3",
        first_name="John",
        last_name="Smith",
    )
    User.create_user(
        username="xwhxycctuyce",
        password="]2[xrCh>",
        first_name="Jane",
        last_name="Doe",
    )
    User.create_user(
        username="qrtdavjtzhwu",
        password="F37ZLv,W",
        first_name="Barack",
        last_name="Obama",
    )
    User.create_user(
        username="vsvvkeqgkczp",
        password="N%2^t<4_",
        first_name="Ada",
        last_name="Lovelace",
    )
    User.create_user(
        username="tvjkgyphhtfw",
        password='Py88"B:$',
        first_name="Edsger",
        last_name="Dijkstra",
    )

    passengers = [
        Passenger(id=1, rating=uniform(0.0, 5.0)),
        Passenger(id=4, rating=uniform(0.0, 5.0)),
    ]

    for passenger in passengers:
        db.session.add(passenger)

    drivers = [
        Driver(id=2, rating=uniform(0.0, 5.0)),
        Driver(id=3, rating=uniform(0.0, 5.0)),
        Driver(id=5, rating=uniform(0.0, 5.0)),
    ]

    for driver in drivers:
        db.session.add(driver)

    db.session.commit()


if __name__ == "__main__":
    main()
