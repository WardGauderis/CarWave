import os
from datetime import datetime, timedelta
from random import uniform

from flask import Flask
from json import loads
from geoalchemy2 import Geometry
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, DatabaseError
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

"""
File with the database models described using SQLAlchemy

TODO:
    - Add more ease of use functions for fulfilling API requests and the like
    - Get rides as a passenger or driver for a user
    - Handle passenger requests for a certain driver
    - How to delete a passenger request?
    - Serialise models to JSON for the API requests?
    - Remove redundant accepted passenger request/ride links vs. 
"""

# The secondary tables for the many-to-many relationships

car_links = db.Table(
    # TODO: Cascade on delete
    "car_links",
    db.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("car_license_plate", db.String, db.ForeignKey("cars.license_plate"), primary_key=True),
)

ride_links = db.Table(
    # TODO: Cascade on delete
    # is dit geen overbodige informatie als er al en tabel is met accepted requests?
    "ride_links",
    db.metadata,
    db.Column("ride_id", db.Integer, db.ForeignKey("rides.id"), primary_key=True),
    db.Column(
        "passenger_id", db.Integer, db.ForeignKey("passengers.id"), primary_key=True
    ),
)


class PassengerRequest(db.Model):
    __tablename__ = "passenger_requests"

    ride_id = db.Column(db.Integer, db.ForeignKey("rides.id"), primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey("passengers.id"), primary_key=True)
    status = db.Column(db.Enum("accepted", "pending", "declined", name="status_enum"), default="pending",
                       nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    last_modified = db.Column(db.DateTime, default=datetime.utcnow())

    ride = db.relationship(
        "Ride", backref=db.backref("rides", cascade="all, delete-orphan")
    )
    passenger = db.relationship(
        "Passenger", backref=db.backref("passengers", cascade="all, delete-orphan")
    )

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

    rides = db.relationship("Ride", back_populates="driver")
    cars = db.relationship("Car", secondary=car_links, back_populates="owners")

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

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def from_username(username: str):
        return User.query.filter_by(username=username).one_or_none()


class Passenger(db.Model):
    """
    Passenger is a User
    """

    __tablename__ = "passengers"

    id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True,
    )
    rating = db.Column(
        db.Numeric(precision=2, scale=1),
        db.CheckConstraint("0.0 <= rating AND rating <= 5.0"),
        default=None,
        nullable=True,
    )
    num_ratings = db.Column(db.Integer, default=0, nullable=False)

    user = db.relationship(
        "User", backref=db.backref("passenger", uselist=False, passive_deletes=True),
    )
    rides = db.relationship("Ride", secondary=ride_links, back_populates="passengers")
    requests = db.relationship(
        "Ride", secondary="passenger_requests", back_populates="requests"
    )

    def __repr__(self):
        return f"<Passenger(id={self.id}, rating={self.rating})>"

    def to_json(self):
        return {"id": self.id, "username": self.user.username}


class Ride(db.Model):
    __tablename__ = "rides"

    id = db.Column(db.Integer, primary_key=True)

    driver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    driver = db.relationship("User", back_populates="rides")
    passenger_places = db.Column(
        db.Integer,
        # TODO: driver counts as one so there should be space for at least one more
        # TODO: len(ride.passengers) <= passenger_places
        db.CheckConstraint("passenger_places >= 2"),
        nullable=False,
    )

    # car_license_plate = db.Column(
    #     db.String(16),
    #     db.ForeignKey("cars.license_plate"),
    #     # db.CheckConstraint("passenger_places <= car"),
    #     nullable=True,
    # )
    # car = db.relationship("Car")

    request_time = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=True)
    departure_address = db.Column(Geometry("POINT", srid=4326), nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    arrival_address = db.Column(Geometry("POINT", srid=4326), nullable=False)

    passengers = db.relationship(
        "Passenger",
        secondary=ride_links,
        back_populates="rides"
    )
    requests = db.relationship(
        "Passenger", secondary="passenger_requests", back_populates="requests"
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
               departure=None,
               departure_distance=1000,
               arrival=None,
               arrival_distance=1000,
               arrival_time=None,
               time_delta=timedelta(minutes=30)):
        """
        Departure/arrival = tuple of 2 floats (longitude, latitude)
        """
        query = Ride.query
        # https://stackoverflow.com/questions/20803878/geoalchemy2-query-all-users-within-x-meteres
        # https://stackoverflow.com/questions/8444753/st-dwithin-takes-parameter-as-degree-not-meters-why
        if departure:
            query = query.filter(func.ST_DWithin(Ride.departure_address, departure, departure_distance, True))
        if arrival:
            query = query.filter(func.ST_DWithin(Ride.arrival_address, arrival, arrival_distance, True))
        if arrival_time:
            query = query.filter(Ride.arrival_time.between(
                arrival_time - time_delta,
                arrival_time + time_delta
            ))
        # Sort by distance to departure/arrival?
        # Move the limit out, only really needed for the API AFAIK
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
    # TODO: # of passengers driver counts as one of the passengers
    passenger_places = db.Column(
        db.Integer, db.CheckConstraint("passenger_places >= 2"), nullable=False
    )

    owners = db.relationship("User", secondary=car_links, back_populates="cars")

    def __repr__(self):
        return f"<Car(license_plate={self.license_plate}, passenger_places={self.passenger_places})>"


def add_entities():
    User.create(
        username="dbsrxvqujuce",
        password="$N:K]r3",
        firstname="John",
        lastname="Smith",
    )
    User.create(
        username="xwhxycctuyce",
        password="]2[xrCh>",
        firstname="Jane",
        lastname="Doe",
    )
    User.create(
        username="qrtdavjtzhwu",
        password="F37ZLv,W",
        firstname="Barack",
        lastname="Obama",
    )
    User.create(
        username="vsvvkeqgkczp",
        password="N%2^t<4_",
        firstname="Ada",
        lastname="Lovelace",
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

    passengers = [
        Passenger(id=1, rating=uniform(0.0, 5.0)),
        Passenger(id=2, rating=uniform(0.0, 5.0)),
        Passenger(id=4, rating=uniform(0.0, 5.0)),
    ]

    for passenger in passengers:
        db.session.add(passenger)

    db.session.add_all(
        [
            Car(
                license_plate="1-QDE-002",
                model="Volkswagen Golf",
                colour="Red",
                passenger_places=5,
            ),
            Car(
                license_plate="5-THX-435",
                model="Renault Clio",
                colour="Black",
                passenger_places=5,
            ),
        ]
    )
    db.session.commit()

    driver1 = User.from_username("xwhxycctuyce")
    driver1.cars.append(
        Car(
            license_plate="8-ABC-001",
            model="Audi R8",
            colour="White",
            passenger_places=2,
        )
    )

    db.session.commit()

    db.session.add(

        Ride.create(
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
    db.session.add(
        Ride.create(
            driver_id=5,
            passenger_places=3,
            arrival_time="2020-02-24T10:43:42.00",
            departure_address=[51.184374, 4.420656],
            arrival_address=[51.219636, 4.403119],
        )
    )
    db.session.commit()

    ride = Ride.query.get(2)
    ride.requests.append(Passenger.query.get(4))
    ride.requests.append(Passenger.query.get(1))
    db.session.commit()

    ride_requests = Ride.query.get(2).requests
    ride_requests.remove(Passenger.query.get(1))
    db.session.commit()

    ride = Ride.query.get(1)
    ride.accepted_requests.append(Passenger.query.get(4))
    ride.accepted_requests.append(Passenger.query.get(1))
    db.session.commit()

def main():
    # add_entities()
    time = datetime(year=2020, month=2, day=24, hour=10, minute=38, second=42)
    delta = timedelta(minutes=4, seconds=60)
    rides = Ride.search(arrival_time=time, time_delta=delta)
    for ride in rides:
        print(ride.arrival_time)



if __name__ == "__main__":
    main()
