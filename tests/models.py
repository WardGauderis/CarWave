import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.crud import search_drives, create_message, read_messages_from_user_pair, read_messaged_users
from app.models import Car, Message, PassengerRequest, Review, Ride, Tag, User

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

with app.app_context():
    rides = search_drives(
        departure=["51.44855695", "5.45012252185714"],
        # departure_distance=2000,
        arrival=["50.879202", "4.7011675"],
        # age_range=(18, 70),
        # sex="male",
        # arrival_time=datetime(year=2020, month=4, day=29, hour=14, minute=1, second=42, tzinfo=tzutc()),
        # arrival_delta=timedelta(minutes=5),
        exclude_past_rides=True,
    )
    # user_id = 3
    # users_messaged = db.session.query(Message.recipient_id).filter(Message.sender_id == user_id).distinct().all()
    # users_messaged = User.query.filter(User.id.in_(users_messaged)).all()
    users = [User.query.get(3), User.query.get(1)]
    messages = read_messages_from_user_pair(*users)
    users_messaged = read_messaged_users(User.query.get(3))
    print("hold")