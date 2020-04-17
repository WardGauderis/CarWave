import json

from flask import Response, abort, request, g

from app.api import bp
from app.auth.auth import token_auth
from app.models import Ride, PassengerRequest
from app.crud import create_user, read_user_from_login, read_drive_from_id, create_drive, create_passenger_request, \
    update_passenger_request
from app.auth.forms import RegistrationForm, LoginForm
from app.offer.forms import OfferForm


@bp.route("/users/register", methods=["POST"])
def register_user():
    json = request.get_json() or {}
    form = RegistrationForm()
    if form.from_json(json):
        user = create_user(form)
        return {"id": user.id}, 201
    abort(409, form.get_errors())


@bp.route("/users/auth", methods=["POST"])
def authorize_user():
    json = request.get_json() or {}
    form = LoginForm()
    if form.from_json(json):
        user = read_user_from_login(form)
        if user:
            token = user.get_token()
            return {"token": token}, 200
        abort(401, "Invalid authorization")
    abort(409, form.get_errors())


@bp.route("/drives", methods=["POST"])
@token_auth.login_required
def register_drive():
    json = request.get_json() or {}
    form = OfferForm()
    if form.from_json(json):
        driver = g.current_user
        drive = create_drive(form, driver)
        return (
            {
                "id": drive.id,
                "driver-id": drive.driver_id,
                "passenger-ids": [],
                "passenger-places": drive.passenger_places,
                "from": drive.depart_from,
                "to": drive.arrive_at,
                "arrive-by": drive.arrival_time,
            },
            201,
            {"Location": f"/drives/{drive.id}"}
        )
    abort(409, form.get_errors())


@bp.route("/drives/<int:drive_id>", methods=["GET"])
def get_drive(drive_id: int):
    ride = read_drive_from_id(drive_id)

    if ride is None:
        abort(404, "Invalid drive id")

    return (
        {
            "id": ride.id,
            "driver-id": ride.driver_id,
            "passenger-ids": [
                passenger.id for passenger in ride.passengers
            ],
            "passenger-places": ride.passenger_places,
            "from": -1,  # TODO format
            "start": -1,
            "arrive-by": ride.arrival_time,
        },
        200,
    )


@bp.route("/drives/<int:drive_id>/passengers", methods=["GET"])
def get_passengers(drive_id):
    ride = read_drive_from_id(drive_id)

    if ride is None:
        abort(400, "Invalid drive id")

    return Response(
        json.dumps([passenger.to_json() for passenger in ride.passengers()]),
        status=200,
        mimetype="application/json"
    )


@bp.route("/drives/<int:drive_id>/passenger-requests", methods=["GET", "POST"])
@token_auth.login_required
def passenger_requests(drive_id):
    ride: Ride = read_drive_from_id(drive_id)
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
        p_request = create_passenger_request(user, ride)
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
    ride = read_drive_from_id(drive_id)
    if ride is None:
        abort(400, f"Drive {drive_id} doesn't exist.")
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
            abort(404, "No such passenger request")

        p_request = update_passenger_request(p_request, action)

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


# TODO search drive -> doe dit in de crud functie search_drives() zodate de site dit ook kan gebruiken
@bp.route("/drives/search", methods=["GET"])
def search_drive():
    MIN_RIDES = 1
    MAX_RIDES = 25
    DEFAULT_LIMIT = 5
    try:
        # Clamp if present, else use default value of 5
        limit = request.args.get("limit")
        # TODO: support these search parameters (https://postgis.net/docs/ST_DWithin.html)
        # Default distances from given start and stop, should be optional
        start = json.get("from")
        stop = json.get("to")
        arrive_by = json.get("arrive-by")
    except KeyError:
        abort(400, "Invalid format")
    if limit:
        limit = max(MIN_RIDES, min(int(limit), MAX_RIDES))
    rides = Ride.search(limit=limit, departure=start, arrival=stop, arrival_time=arrive_by)
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
