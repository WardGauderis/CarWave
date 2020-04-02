import json

from flask import Response, abort, request, g
from sqlalchemy.exc import DatabaseError

from app.api import bp
from app.auth.auth import token_auth
from app.models import Ride, User, PassengerRequest


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

    user = User.create(
        username=username, first_name=first_name, last_name=last_name, password=password
    )
    if isinstance(user, DatabaseError):
        abort(400, user.statement)
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
    json = request.get_json() or {}
    try:
        start = json["from"]
        stop = json["to"]
        passenger_places = json["passenger-places"]
        arrive_by = json["arrive-by"]
    except KeyError:
        abort(400, "Invalid format")

    user = g.current_user
    ride = Ride.create(
        driver_id=user.id,
        passenger_places=passenger_places,
        departure_address=start,
        arrival_address=stop,
        arrival_time=arrive_by,
    )
    if isinstance(ride, DatabaseError):
        abort(500, ride.statement)

    return (
        {
            "id": ride.id,
            "driver-id": ride.driver_id,
            "passenger-ids": [],
            "passenger-places": ride.passenger_places,
            "from": ride.depart_from,
            "to": ride.arrive_at,
            "arrive-by": ride.arrival_time,
        },
        201,
        {"Location": f"/drives/{ride.id}"}
    )


@bp.route("/drives/<int:drive_id>", methods=["GET"])
def get_drive(drive_id: int):
    ride = Ride.get(drive_id)

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
    ride = Ride.get(drive_id)

    if ride is None:
        abort(400, "Invalid drive id")

    return Response(
        json.dumps([passenger.to_json() for passenger in ride.passengers]),
        status=200,
        mimetype="application/json"
    )


@bp.route("/drives/<int:drive_id>/passenger-requests", methods=["GET", "POST"])
@token_auth.login_required
def passenger_requests(drive_id):
    ride: Ride = Ride.get(drive_id)
    if ride is None:
        abort(400, f"Drive {drive_id} doesn't exist.")

    user = g.current_user
    if request.method == "GET":
        if ride.driver_id == user.id:
            return Response(
                json.dumps([
                    {
                        "id": p_request.passenger_id,
                        "username": p_request.passenger.user.username,
                        "status": p_request.status,
                        "time-created": p_request.created_at.isoformat(),
                    }
                    for p_request in ride.requests
                ]),
                status=200,
                mimetype="application/json"
            )
        else:
            abort(401, "Invalid authorization")
    else:  # POST
        p_request = ride.post_passenger_request(user.id)
        if isinstance(p_request, DatabaseError):
            abort(500, p_request.statement)

        return (
            {
                "id": p_request.passenger_id,
                "username": p_request.passenger.user.username,
                "status": p_request.status,
                "time-created": p_request.created_at.isoformat(),
            },
            201,
            {"Location": f"/drives/{p_request.ride_id}/passenger-requests/{p_request.passenger_id}"},
        )


@bp.route("/drives/<int:drive_id>/passenger-requests/<int:user_id>", methods=["POST"])
@token_auth.login_required
def accept_passenger_request(drive_id, user_id):
    ride = Ride.get(drive_id)
    user = g.current_user
    if ride.driver_id == user.id:
        json = request.get_json() or {}
        try:
            action = json["action"]
        except KeyError:
            abort(400, "Invalid format")

        if action not in ["accept", "reject"]:
            abort(400, "Invalid action")

        p_request = PassengerRequest.query.get((ride.id, user_id))
        if p_request is None:
            abort(400, "No such passenger request")
        elif p_request.status != "pending":
            abort(400, "This request has already been accepted or declined")

        p_request = p_request.update(action)

        return (
            {
                "id": p_request.passenger_id,
                "username": p_request.passenger.user.username,
                "status": p_request.status,
                "time-created": p_request.created_at.isoformat(),
                "time-updated": p_request.last_modified.isoformat(),
            },
            200,
        )
    else:
        abort(401, "Invalid authorization")


@bp.route("/drives/search", methods=["GET"])  # TODO search drive
def search_drive():
    MIN_RIDES = 1
    MAX_RIDES = 25
    DEFAULT_LIMIT = 5
    try:
        # Clamp if present, else use default value of 5
        limit = request.args.get("limit")
        # TODO: support these search parameters (https://postgis.net/docs/ST_DWithin.html)
        # start = json["from"]
        # stop = json["to"]
        # arrive_by = json["arrive-by"]
    except KeyError:
        abort(400, "Invalid format")

    limit = DEFAULT_LIMIT if limit is None else max(MIN_RIDES, min(int(limit), MAX_RIDES))
    rides = Ride.get_all(limit)
    return Response(
        json.dumps([
            {
                "id": ride.id,
                "driver-id": ride.driver_id,
                "passenger-ids": [passenger.id for passenger in ride.passengers],
                "from": ride.depart_from,
                "to": ride.arrive_at,
                "arrive-by": ride.arrival_time.isoformat(),
            }
            for ride in rides
        ]),
        status=200,
        mimetype="application/json"
    )
