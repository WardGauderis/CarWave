from app import db, login
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask import current_app
import datetime
from flask_login import UserMixin


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


class CarLinks(db.Model):
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


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    first_name = db.Column(db.VARCHAR, nullable=False)
    last_name = db.Column(db.VARCHAR, nullable=False)
    created_at = db.Column(db.TIMESTAMP)
    home_adress_id = db.Column(db.Integer, ForeignKey("adresses.adress_id"))
    phone_number = db.Column(db.Integer)
    email_adress = db.Column(db.String(128))

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def from_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def from_token(token):
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return User.query.get(data['id'])
        except:
            return None

    def get_token(self):
        return jwt.encode({'id': self.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                          current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))


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
