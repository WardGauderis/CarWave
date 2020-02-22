from app import db
# from datetime import datetime
# from typing import List

"""
File with the database models described using SQLAlchemy
"""

# Entities


class User(db.Model):
    """
    """

    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime)
    # TODO: double check foreign key declaration, db.relationship(...)
    # address_id = db.Column(db.Integer)  # TODO: FK
    phone_number = db.Column(db.String)

    @staticmethod
    def get_user(user_id: int):
        return None


class Driver(User):
    """
    Driver is a User
    """

    rating = db.column(db.Integer, nullable=False)


class Passenger(User):
    """
    Passenger is a User
    """

    rating = db.column(db.Integer, nullable=False)


class Ride(db.Model):
    """
    """

    __tablename__ = "rides"
    ride_id = db.Column(db.Integer, primary_key=True)
    # driver_id = db.relationship() one2m
    # passenger_id = db.relationship() m2m
    request_time = db.Column(db.DateTime)
    departure_time = db.Column(db.DateTime)
    arrival_time = db.Column(db.DateTime)


class Address(db.Model):
    """
    """
    __tablename__ = "addresses"
    address_id = db.Column(db.Integer, primary_key=True)


class Car(db.Model):
    """
    """

    __tablename__ = "cars"
    license_plate = db.column(db.String, primary_key=True)
    model = db.column(db.String, nullable=True)
    colour = db.column(db.String, nullable=True)
    num_passengers = db.column(db.Integer, nullable=False)


# Relationships


class Belongs(db.Model):
    driver_id = # FK
    license_plate = # F
