import json

from flask import Response, abort, request

from app.api import bp
from app.auth.auth import token_auth
from app.models import Ride, User


@bp.route("/users/register", methods=["POST"])
def register_user():
    json = request.get_json() or {}
    try:
        username = json["username"]
        first_name = json["firstname"]
        last_name = json["lastname"]
        password = json["password"]
    except KeyError:
        abort(400, "Invalid format")

    user = User.create_user(
        username=username, first_name=first_name, last_name=last_name, password=password
    )
    if user is None:
        abort(400, "This username is already in use")
    return {"id": user.id}, 201


@bp.route("/users/auth", methods=["POST"])
def authorize_user():
    json = request.get_json() or {}
    try:
        username = json["username"]
        password = json["password"]
    except KeyError:
        abort(400, "Invalid format")

    user = User.from_username(username)
    if user is not None and user.check_password(password):
        token = user.get_token()
        return {"token": token}, 200
    else:
        abort(401, "Invalid authorization")


@bp.route("/drives", methods=["POST"])
@token_auth.login_required
def register_drive():
    # Strip 'Bearer ' prefix
    token = request.headers.environ["HTTP_AUTHORIZATION"][7:]
    json = request.get_json() or {}
    try:
        start = json["from"]
        stop = json["to"]
        passenger_places = json["passenger-places"]
        arrive_by = json["arrive-by"]
    except KeyError:
        abort(400, "Invalid format")

    accepted = True  # TODO(Ward): condition?
    if accepted:
        # TODO: wie kan rides aanmaken? driver, passenger of beide?
        user = User.from_token(token)
        if user.driver is None:
            abort(400, "Rides can only be created by drivers")
        ride = Ride.create_ride(
            driver_id=user.id,
            passenger_places=passenger_places,
            arrival_time=arrive_by
        )
        return (
            {
                "id": ride.id,
                "driver-id": ride.driver_id,
                "passenger-ids": [  # altijd leeg bij registration, neem ik aan?
                    passenger.id for passenger in ride.passengers
                ],
                "passenger-places": ride.passenger_places,
                # "from": address[ride.arrival_address_id],
                # "to": address[ride.departure_address_id],
                "arrive-by": ride.arrival_time,
            },
            201,
            {"Location": f"/drives/{ride.id}"}
        )
    else:
        abort(401, "Invalid authorization")


# FIXME: addressen
@bp.route("/drives/<int:drive_id>", methods=["GET"])
def get_drive(drive_id: int):
    ride = Ride.get_ride(drive_id)

    if ride is None:
        abort(400, "Invalid drive id")

    return (
        {
            "id": ride.id,
            "driver-id": ride.driver_id,
            "passenger-ids": [
                passenger.id for passenger in ride.passengers
            ],
            "passenger-places": ride.passenger_places,
            "from": -1,
            "start": -1,
            "arrive-by": ride.arrival_time,
        },
        200,
    )


@bp.route("/drives/<int:drive_id>/passengers", methods=["GET"])
def get_passengers(drive_id):
    ride = Ride.get_ride(drive_id)

    if ride is None:
        abort(400, "Invalid drive id")

    return Response(
        json.dumps([passenger.to_json() for passenger in ride.passengers]),
        status=200,
        mimetype="application/json"
    )


@bp.route("/drives/<int:drive_id>/passenger-requests", methods=["GET", "POST"])
@token_auth.login_required
def get_passenger_requests(drive_id):
    if request.method == "GET":
        token = request.headers.environ["HTTP_AUTHORIZATION"][7:]
        ride = Ride.get_ride(drive_id)
        user = User.from_token(token)
        if ride.driver_id == user.id:
            return Response(
                json.dumps([
                    {
                        "id": passenger.id,
                        "username": passenger.user.username,
                        # FIXME(Hayaan): shift to enum, e.g. passenger.request.status
                        "status": "pending",
                        "time-created": passenger.user.created_at.isoformat(),
                    }
                    for passenger in ride.requests
                ]),
                status=200,
                mimetype="application/json"
            )
        else:
            abort(401, "Invalid authorization")
    else:  # POST
        # TODO(Hayaan): still need to add a function for this
        accepted = True
        if accepted:
            id = 0
            username = ""
            status = ""
            time_created = ""
            location = f"/drives/{0}/passenger-requests/{0}"
            return (
                {
                    "id": id,
                    "username": username,
                    "status": status,
                    "time-created": time_created,
                },
                201,
                {"Location": location},
            )
        else:
            abort(401, "Invalid authorization")


@bp.route("/drives/<int:drive_id>/passenger-requests/<int:user_id>", methods=["POST"])
@token_auth.login_required
def accept_passenger_request(drive_id, user_id):
    accepted = True
    if accepted:
        json = request.get_json() or {}
        try:
            action = json["action"]
        except KeyError:
            abort(400, "Invalid format")

        id = 0
        username = ""
        status = ""
        time_created = ""
        time_updated = ""
        return (
            {
                "id": id,
                "username": username,
                "status": status,
                "time-created": time_created,
                "time-updated": time_updated,
            },
            200,
        )
    else:
        abort(401, "Invalid authorization")


@bp.route("/drives/search", methods=["GET"])
def search_drive():
    json = request.get_json() or {}
    try:
        limit = request.args["limit"]
        start = json["from"]
        stop = json["to"]
        arrive_by = json["arrive-by"]
    except KeyError:
        abort(400, "Invalid format")

    id = 0
    driver_id = 0
    passenger_ids = []
    return (
        [
            {
                "id": id,
                "driver-id": driver_id,
                "passenger-ids": passenger_ids,
                "from": start,
                "to": stop,
                "arrive-by": arrive_by,
            }
        ],
        200,
    )
