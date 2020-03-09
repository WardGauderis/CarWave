import os
from datetime import datetime

from flask import Flask
from sqlalchemy import func
from flask_login import UserMixin
from json import loads
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
db = SQLAlchemy(app)


"""
File with the database models described using SQLAlchemy

TODO:
    - Add more ease of use functions for fulfilling API requests and the like
    - How to delete a passenger request?
        - Set to declined or move to ride.passengers. Check if if ride.passengers before adding to ride.requests.
    - Serialise models to JSON for the API requests?
"""

# The secondary tables for the many-to-many relationships

car_links = db.Table(
    "car_links",
    db.metadata,
    db.Column("driver_id", db.Integer, db.ForeignKey("drivers.id"), primary_key=True),
    db.Column(
        "car_license_plate",
        db.String,
        db.ForeignKey("cars.license_plate"),
        primary_key=True,
    ),
)

ride_links = db.Table(
    "ride_links",
    db.metadata,
    db.Column("ride_id", db.Integer, db.ForeignKey("rides.id"), primary_key=True),
    db.Column(
        "passenger_id", db.Integer, db.ForeignKey("passengers.id"), primary_key=True
    ),
)


class PassengerRequest(db.Model):
    __tablename__ = "passenger_requests"
    ___tableargs__ = [
        # TODO: CheckConstraint, not present in ride_links
        # TODO: CheckConstraint, not the same
    ]

    ride_id = db.Column(db.Integer, db.ForeignKey("rides.id"), primary_key=True)
    passenger_id = db.Column(
        db.Integer, db.ForeignKey("passengers.id"), primary_key=True
    )
    status = db.Column(
        db.Enum("pending", "declined", name="status_enum"),
        default="pending",
        nullable=False,
    )

    ride = db.relationship(
        "Ride", backref=db.backref("rides", cascade="all, delete-orphan")
    )
    passenger = db.relationship(
        "Passenger", backref=db.backref("passengers", cascade="all, delete-orphan")
    )


# Entities


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email_adress = db.Column(db.String(128))
    address_id = db.Column(db.Integer)
    phone_number = db.Column(db.String(32))
    age = db.Column(db.Integer, db.CheckConstraint("13 <= age AND age <= 200"))
    gender = db.Column(
        db.Enum("male", "female", "other", name="gender_enum"),
        default="male",
        nullable=False,
    )
    # TODO: Gravatar?
    # profile_picture = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

    @staticmethod
    def create(**kwargs) -> int:
        try:
            # TODO: Reject passwords shorter than a specified length. probably in the form
            kwargs["password_hash"] = generate_password_hash(kwargs.pop("password"))
        except KeyError:
            raise ValueError("No 'password' keyword argument was supplied")

        try:
            user = User(**kwargs)
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            return None

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def from_username(username: str):
        return User.query.filter_by(username=username).one_or_none()


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(
        db.Numeric(precision=2, scale=1),
        db.CheckConstraint("0.0 <= rating AND rating <= 5.0"),
        nullable=False,
    )
    text = db.Column(db.String(256), nullable=True)
    reviewee_id = db.Column(
        db.Integer, db.ForeignKey("users.id", on_delete="CASCADE"), nullable=False
    )
    author_id = db.Column(
        db.Integer, db.ForeignKey("users.id", on_delete="CASCADE"), nullable=False
    )

    # TODO: can't review yourself


class Driver(db.Model):
    """
    Driver is a User
    """

    __tablename__ = "drivers"

    id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True,
    )

    user = db.relationship(
        "User", backref=db.backref("driver", uselist=False, passive_deletes=True),
    )
    rides = db.relationship("Ride", back_populates="driver")
    cars = db.relationship("Car", secondary=car_links, back_populates="drivers")

    def __repr__(self):
        return f"<Driver(id={self.id}, rating={self.rating})>"


class Passenger(db.Model):
    """
    Passenger is a User
    """

    __tablename__ = "passengers"

    id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True,
    )

    user = db.relationship(
        "User", backref=db.backref("passenger", uselist=False, passive_deletes=True),
    )
    rides = db.relationship("Ride", secondary=ride_links, back_populates="passengers")
    requests = db.relationship("Ride", secondary="passenger_requests")

    def __repr__(self):
        return f"<Passenger(id={self.id}, rating={self.rating})>"

    def to_json(self):
        return {"id": self.id, "username": self.user.username}


class Ride(db.Model):
    __tablename__ = "rides"

    id = db.Column(db.Integer, primary_key=True)

    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"), nullable=False)
    driver = db.relationship("Driver", back_populates="rides")
    passenger_places = db.Column(
        db.Integer, db.CheckConstraint("passenger_places >= 2"), nullable=False
    )
    # TODO
    # Addable at a later date, but must check car's # of passenger places is
    # greater or equal to the ride's # of passengers
    car_license_plate = db.Column(
        db.String(16),
        db.ForeignKey("cars.license_plate"),
        # db.CheckConstraint("passenger_places <= car"),
        nullable=True,
    )
    car = db.relationship("Car")

    request_time = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    departure_address = db.Column(Geometry("POINT", srid=4326), nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    arrival_address = db.Column(Geometry("POINT", srid=4326), nullable=False)

    passengers = db.relationship(
        "Passenger", secondary="ride_links", back_populates="rides"
    )
    requests = db.relationship("Passenger", secondary="passenger_requests")

    def __repr__(self):
        return f"<Ride(id={self.id}, driver={self.driver_id})>"

    @staticmethod
    def create(**kwargs):
        try:
            # TODO: Move this to the API request handler?
            dep, arr = kwargs.pop("departure_address"), kwargs.pop("arrival_address")
            kwargs["departure_address"] = f"SRID=4326;POINT({dep[0]} {dep[1]})"
            kwargs["arrival_address"] = f"SRID=4326;POINT({arr[0]} {arr[1]})"
            ride = Ride(**kwargs)
            db.session.add(ride)
            db.session.commit()
            return ride
        except KeyError:
            # Throw or error message?
            return None
        except IntegrityError:
            db.session.rollback()
            return None

    @staticmethod
    def get_ride(ride_id: int):
        return Ride.query.get(ride_id)

    # FIXME: should be replaceable with a CheckConstraint
    def add_car(self, car) -> bool:
        if self.passenger_places < car.passenger_places:
            return False
        self.car = car
        db.session.commit()
        return True


class Car(db.Model):
    __tablename__ = "cars"

    license_plate = db.Column(db.String(16), primary_key=True)
    model = db.Column(db.String(128), nullable=False)
    colour = db.Column(db.String(32), nullable=False)
    passenger_places = db.Column(
        db.Integer, db.CheckConstraint("passenger_places >= 2"), nullable=False
    )

    drivers = db.relationship("Driver", secondary="car_links", back_populates="cars")

    def __repr__(self):
        return f"<Car(license_plate={self.license_plate}, passenger_places={self.passenger_places})>"


def main():
    db.drop_all()

    db.create_all()

    User.create(
        username="dbsrxvqujuce",
        password="$N:K]r3",
        first_name="John",
        last_name="Smith",
    )
    # User.create(
    #     username="xwhxycctuyce",
    #     password="]2[xrCh>",
    #     first_name="Jane",
    #     last_name="Doe",
    # )
    # User.create(
    #     username="qrtdavjtzhwu",
    #     password="F37ZLv,W",
    #     first_name="Barack",
    #     last_name="Obama",
    # )
    # User.create(
    #     username="vsvvkeqgkczp",
    #     password="N%2^t<4_",
    #     first_name="Ada",
    #     last_name="Lovelace",
    # )
    # User.create(
    #     username="tvjkgyphhtfw",
    #     password='Py88"B:$',
    #     first_name="Edsger",
    #     last_name="Dijkstra",
    # )
    # # Duplicate username, what happens?
    # # User.create(
    # #     username="tvjkgyphhtfw",
    # #     password='Py88"B:$',
    # #     first_name="Edsger",
    # #     last_name="Dijkstra",
    # # )

    # passengers = [Passenger(id=1), Passenger(id=4)]

    # for passenger in passengers:
    #     db.session.add(passenger)

    db.session.add(Driver(id=1))
    db.session.commit()
    # db.session.add_all([Driver(id=2), Driver(id=3), Driver(id=5)])
    # db.session.add_all(
    #     [
    #         Car(
    #             license_plate="1-QDE-002",
    #             model="Volkswagen Golf",
    #             colour="Red",
    #             passenger_places=5,
    #         ),
    #         Car(
    #             license_plate="5-THX-435",
    #             model="Renault Clio",
    #             colour="Black",
    #             passenger_places=5,
    #         ),
    #     ]
    # )
    # db.session.commit()

    # driver1 = User.from_username("xwhxycctuyce").driver
    # driver1.cars.append(
    #     Car(
    #         license_plate="8-ABC-001",
    #         model="Audi R8",
    #         colour="White",
    #         passenger_places=2,
    #     )
    # )

    # db.session.commit()

    # db.session.add_all(
    #     [
    #         # Ride(driver_id=5, car_license_plate="5-THX-435"), # should fail
    #         Ride(
    #             driver_id=2,
    #             passenger_places=3,
    #             car_license_plate="8-ABC-001",
    #             arrival_time="2020-02-12T10:00:00.00",
    #         ),
    #     ]
    # )
    # db.session.commit()

    # driver2 = User.query.get(5).driver
    # driver2.cars.append(Car.query.get("5-THX-435"))
    # db.session.commit()

    # # should fail
    # # db.session.add(Ride(driver_id=5, car_license_plate="1-QDE-002"))
    # # db.session.commit()

    # # should work
    # db.session.add(
    #     Ride(
    #         driver_id=5,
    #         passenger_places=3,
    #         arrival_time="2020-02-12T10:00:00.00",
    #         car_license_plate="5-THX-435",
    #     )
    # )
    # db.session.commit()

    # ride = Ride.query.get(2)
    # ride.requests.append(Passenger.query.get(4))
    # ride.requests.append(Passenger.query.get(1))
    # db.session.commit()

    # ride_requests = Ride.query.get(2).requests
    # ride_requests.remove(Passenger.query.get(1))
    # db.session.commit()

    # ride = Ride.query.get(1)
    # ride.passengers.append(Passenger.query.get(4))
    # ride.passengers.append(Passenger.query.get(1))
    # db.session.commit()

    # query = db.session.query(PassengerRequest).filter_by(ride_id=2).all()
    Ride.create(
            driver_id=1,
            passenger_places=3,
            departure_address=[51.130215, 4.571509],
            arrival_address=[51.18417, 4.41931],
            arrival_time="2020-02-12T10:00:00.00",
    )
    db.session.commit()
    ride = Ride.query.first()
    point = loads(db.session.scalar(func.ST_AsGeoJson(ride.arrival_address)))
    coords = point["coordinates"]


if __name__ == "__main__":
    main()
