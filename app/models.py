from app import db
from sqlalchemy import ForeignKey

"""
File with the database models described using SQLAlchemy
"""


class Driver(db.Model):
    __tablename__ = 'drivers'
    driver_id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)

    def __init__(self, driver_id):
        self.driver_id = driver_id

    def __repr__(self):
        return '<id {}>'.format(self.driver_id)


class Passenger(db.Model):
    __tablename__ = 'passengers'
    passenger_id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)

    def __init__(self, passenger_id):
        self.passenger_id = passenger_id

    def __repr__(self):
        return '<id {}>'.format(self.passenger_id)


class Adress(db.Model):
    __tablename__ = 'adresses'
    adress_id = db.Column(db.Integer, primary_key=True)
    adress_name = db.Column(db.VARCHAR, nullable=False)

    def __init__(self, adress_id, adress_name):
        self.adress_name = adress_name
        self.adress_id = adress_id

    def __repr__(self):
        return '<id {}>'.format(self.adress_id)


class Car_Links(db.Model):
    __tablename__ = 'car_links'
    driver_id = db.Column(db.Integer, ForeignKey("drivers.driver_id"), nullable=False, primary_key=True)
    license_plate = db.Column(db.VARCHAR, ForeignKey("cars.license_plate"), nullable=False, primary_key=True)

    def __init__(self, driver_id, license_plate):
        self.driver_id = driver_id
        self.license_plate = license_plate

    def __repr__(self):
        return '<id {}>'.format(self.license_plate)


class Cars(db.Model):
    __tablename__ = 'cars'
    license_plate = db.Column(db.VARCHAR, primary_key=True)
    model = db.Column(db.VARCHAR, nullable=False)
    color = db.Column(db.VARCHAR, nullable=False)
    num_passengers = db.Column(db.Integer, nullable=False)

    def __init__(self, model, license_plate, color, num_passengers):
        self.model = model
        self.color = color
        self.num_passengers = num_passengers
        self.license_plate = license_plate

    def __repr__(self):
        return '<id {}>'.format(self.license_plate)


class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.VARCHAR, nullable=False)
    last_name = db.Column(db.VARCHAR, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    home_adress_id = db.Column(db.Integer, ForeignKey("adresses.adress_id"), nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, first_name, last_name, created_at, home_adress_id, phone_number):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = created_at
        self.home_adress_id = home_adress_id
        self.phone_number = phone_number

    def __repr__(self):
        return '<id {}>'.format(self.user_id)


class Rides(db.Model):
    __tablename__ = 'rides'
    ride_id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, ForeignKey("drivers.driver_id"))
    passenger_id = db.Column(db.Integer, ForeignKey("passengers.passenger_id"), nullable=False)
    request_time = db.Column(db.TIMESTAMP, nullable=False)
    departure_time = db.Column(db.TIMESTAMP)
    arrival_time = db.Column(db.TIMESTAMP)
    departure_adress_id = db.Column(db.Integer, ForeignKey("adresses.adress_id"), nullable=False)
    arrival_adress_id = db.Column(db.Integer, ForeignKey("adresses.adress_id"), nullable=False)

    def __init__(self, ride_id, passenger_id, request_time, departure_adress_id, arrival_adress_id):
        self.ride_id = ride_id
        self.passenger_id = passenger_id
        self.request_time = request_time
        self.departure_adress_id = departure_adress_id
        self.arrival_adress_id = arrival_adress_id

    def __repr__(self):
        return '<id {}>'.format(self.user_id)
