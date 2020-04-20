import os
from datetime import datetime, timedelta
from hashlib import md5
from json import loads

import requests
from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from sqlalchemy import func
from sqlalchemy.exc import DatabaseError, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class PassengerRequest(db.Model):
    __tablename__ = "passenger_requests"

    ride_id = db.Column(db.Integer, db.ForeignKey("rides.id", ondelete='CASCADE'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='CASCADE'), primary_key=True)
    status = db.Column(db.Enum("accepted", "pending", "rejected", name="status_enum"), default="pending",
                       nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    last_modified = db.Column(db.DateTime, default=datetime.utcnow())

    ride = db.relationship("Ride", back_populates="requests", single_parent=True)
    passenger = db.relationship("User", back_populates="requests", single_parent=True)

    def update(self, action):
        if action == "accept":
            self.ride.accepted_requests.append(self.passenger)
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
    age = db.Column(db.Integer, nullable=True)
    sex = db.Column(db.Enum("male", "female", "non-binary", name="sex_enum"), nullable=True)
    address_id = db.Column(db.String(32), nullable=True)

    driver_rides = db.relationship("Ride", back_populates="driver", cascade="all, delete, delete-orphan")
    cars = db.relationship("Car", back_populates="owner", cascade="all, delete, delete-orphan")

    requests = db.relationship(
        "PassengerRequest", back_populates="passenger", lazy="dynamic", cascade="all, delete, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

    @staticmethod
    def create(**kwargs):
        try:
            kwargs["password_hash"] = generate_password_hash(kwargs.pop("password"))
        except KeyError:
            raise ValueError("No 'password' keyword argument was supplied")

        try:
            user = User(**kwargs)
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError as e:
            db.session.rollback()
            return e

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def from_form(self, form):
        for key, value in form.generator():
            setattr(self, key, value)
        if not form.update:
            self.set_password(form.password.data)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

    def passenger_rides(self):
        return self.requests.filter_by(status="accepted").all()

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def from_username(username: str):
        return User.query.filter_by(username=username).one_or_none()

class Ride(db.Model):
    __tablename__ = "rides"

    id = db.Column(db.Integer, primary_key=True)

    driver_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    driver = db.relationship("User", back_populates="driver_rides", single_parent=True)
    passenger_places = db.Column(db.Integer, nullable=False)

    license_plate = db.Column(db.String(16), db.ForeignKey("cars.license_plate", ondelete='SET NULL'), nullable=True)
    car = db.relationship("Car", back_populates="rides")

    request_time = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=True)
    departure_address = db.Column(Geometry("POINT", srid=4326), nullable=False)
    departure_id = db.Column(db.String(32), nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    arrival_address = db.Column(Geometry("POINT", srid=4326), nullable=False)
    arrival_id = db.Column(db.String(32), nullable=False)

    requests = db.relationship(
        "PassengerRequest", back_populates="ride", lazy="dynamic", cascade="all, delete, delete-orphan"
    )

    def __repr__(self):
        return f"<Ride(id={self.id}, driver={self.driver_id})>"

    @staticmethod
    def create(**kwargs):
        try:
            dep, arr = kwargs.pop("departure_address"), kwargs.pop("arrival_address")
            kwargs["departure_address"] = f"SRID=4326;POINT({dep[0]} {dep[1]})"
            kwargs["arrival_address"] = f"SRID=4326;POINT({arr[0]} {arr[1]})"
            ride = Ride(**kwargs)
            db.session.add(ride)
            db.session.commit()
            return ride
        except DatabaseError as e:
            db.session.rollback()
            return e

    @staticmethod
    def get(ride_id: int):
        return Ride.query.get(ride_id)

    @staticmethod
    def search(limit=5,
               departure=None, departure_distance=1000,
               arrival=None, arrival_distance=1000,
               departure_time=None, departure_delta=timedelta(minutes=30),
               arrival_time=None, arrival_delta=timedelta(minutes=30),
               sex=None, age_range=None, consumption_range=None):
        """
        Departure/arrival = tuple of 2 floats (longitude, latitude)
        """
        query = Ride.query
        if departure:
            query = query.filter(func.ST_DWithin(Ride.departure_address, departure, departure_distance, True))
        if arrival:
            query = query.filter(func.ST_DWithin(Ride.arrival_address, arrival, arrival_distance, True))
        # FIXME: don't think we need to worry about handling rows with a NULL
        #        value, if the user cares about rides with a specific departure time then
        #        they likely wouldn't want to see rides without a specified departure time
        if departure_time:
            query = query.filter(Ride.departure_time.between(
                departure_time - departure_delta,
                departure_time + departure_delta
            ))
        if arrival_time:
            query = query.filter(Ride.arrival_time.between(
                arrival_time - arrival_delta,
                arrival_time + arrival_delta
            ))
        if sex:  # (͡°͜ʖ͡°)
            if sex not in ["male", "female", "non-binary"]:
                raise ValueError("Invalid sex")
            # query = query.filter(Ride.driver.has(sex=sex))
            query = query.join(Ride.driver).filter_by(sex=sex)

        # Allow (min, None) (None, max) & (min, max) for ranges
        # TODO(Hayaan): Age filter
        if age_range:
            pass
        # TODO(Hayaan): Consumption filter
        if consumption_range:
            pass

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
            return data.osm_type + data.osm_id

        if not form.arrival_id.data:
            self.arrival_id = location_to_id(form.to_lon.data, form.to_lat.data)
        if not form.departure_id.data:
            self.arrival_id = location_to_id(form.from_lon.data, form.from_lat.data)

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
    consumption = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    owner = db.relationship("User", back_populates="cars", single_parent=True)
    rides = db.relationship("Ride", back_populates="car")

    def __repr__(self):
        return f"<Car(license_plate={self.license_plate}, passenger_places={self.passenger_places})>"

    def from_form(self, form):
        for key, value in form.generator():
            setattr(self, key, value)


def add_entities():
    User.create(
        username="dbsrxvqujuce",
        password="$N:K]r3",
        firstname="John",
        lastname="Smith",
        sex="male",
    )
    User.create(
        username="xwhxycctuyce",
        password="]2[xrCh>",
        firstname="Jane",
        lastname="Doe",
        sex="female",
    )
    User.create(
        username="qrtdavjtzhwu",
        password="F37ZLv,W",
        firstname="Barack",
        lastname="Obama",
        sex="male",
    )
    User.create(
        username="vsvvkeqgkczp",
        password="N%2^t<4_",
        firstname="Ada",
        lastname="Lovelace",
        sex="female",
    )
    User.create(
        username="tvjkgyphhtfw",
        password='Py88"B:$',
        firstname="Edsger",
        lastname="Dijkstra",
    )
    # Duplicate username, what happens?
    User.create(
        username="tvjkgyphhtfw",
        password='Py88"B:$',
        firstname="Edsger",
        lastname="Dijkstra",
    )

    db.session.add_all(
        [
            Car(
                license_plate="1-QDE-002",
                user_id=2,
                model="Volkswagen Golf",
                colour="Red",
                passenger_places=5,
                build_year=2000,
                fuel="diesel",
                consumption=1,
            ),
            Car(
                license_plate="5-THX-435",
                user_id=2,
                model="Renault Clio",
                colour="Black",
                passenger_places=5,
                build_year=2000,
                fuel="diesel",
                consumption=1,
            ),
        ]
    )
    db.session.commit()

    driver1 = User.from_username("xwhxycctuyce")
    driver1.cars.append(
        Car(
            license_plate="8-ABC-001",
            user_id=1,
            model="Audi R8",
            colour="White",
            passenger_places=2,
            build_year=2000,
            fuel="diesel",
            consumption=1,
        )
    )

    db.session.commit()

    db.session.add(

        Ride.create(
            arrival_id="something",
            departure_id="testing",
            driver_id=2,
            passenger_places=3,
            arrival_time="2020-02-12T10:00:00.00",
            departure_address=[51.184374, 4.420656],
            arrival_address=[50.880623, 4.700622],
        )
    )
    db.session.commit()

    driver2 = User.query.get(5)
    driver2.cars.append(Car.query.get("5-THX-435"))
    db.session.commit()

    # should fail
    # db.session.add(Ride.create(driver_id=5, car_license_plate="1-QDE-002"))
    # db.session.commit()

    # should work
    db.session.add_all([
        Ride.create(
            arrival_id="something",
            departure_id="testing",
            driver_id=1,
            passenger_places=3,
            arrival_time="2020-02-24T10:43:42.00",
            departure_address=[51.184374, 4.420656],
            arrival_address=[51.219636, 4.403119],
        ),
        Ride.create(
            arrival_id="something",
            departure_id="testing",
            driver_id=4,
            passenger_places=4,
            arrival_time="2020-10-12T09:00:00.00",
            departure_address=[50.115498, 4.625988],
            arrival_address=[51.184374, 4.420656],
        ),
        Ride.create(
            arrival_id="something",
            departure_id="testing",
            driver_id=5,
            passenger_places=1,
            arrival_time="2020-10-12T18:15:00.00",
            departure_address=[51.184374, 4.420656],
            arrival_address=[50.115498, 4.625988],
        ),
    ])
    db.session.commit()


def main():
    # add_entities()
    all_rides = Ride.query.all()
    time = datetime(year=2020, month=2, day=24, hour=10, minute=38, second=42)
    delta = timedelta(minutes=4, seconds=60)
    rides = Ride.search(
        # arrival_time=time,
        # time_delta=delta,
        sex=None
    )
    for ride in rides:
        print(ride.driver.sex)
        print(ride.arrival_time)



if __name__ == "__main__":
    # main()
    db.drop_all()
    db.create_all()
    add_entities()