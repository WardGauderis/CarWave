import json
from datetime import datetime, timedelta, date

from flask import Response, abort, request, g

from app.api import bp
from app.auth.auth import token_auth
from app.models import Ride, PassengerRequest
from app.crud import create_user, read_user_from_login, read_drive_from_id, create_drive, create_passenger_request, \
    update_passenger_request, search_drives
from app.auth.forms import UserForm, LoginForm
from app.offer.forms import OfferForm


@bp.route("/users/register", methods=["POST"])
def register_user():
    json = request.get_json() or {}
    form = UserForm()
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
                request.user_id for request in ride.accepted_requests()
            ],
            "passenger-places": ride.passenger_places,
            "from": ride.depart_from,
            "to": ride.arrive_at,
            "arrive-by": ride.arrival_time.isoformat(),
        },
        200,
    )


@bp.route("/drives/<int:drive_id>/passengers", methods=["GET"])
def get_passengers(drive_id):
    ride = read_drive_from_id(drive_id)

    if ride is None:
        abort(400, "Invalid drive id")

    return Response(
        json.dumps(
            [{"id": request.user_id, "username": request.passenger.username} for request in ride.accepted_requests()]),
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
        if ride.driver == user:
            return Response(
                json.dumps([
                    {
                        "id": p_request.user_id,
                        "username": p_request.passenger.username,
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
                "id": p_request.user_id,
                "username": p_request.passenger.username,
                "status": p_request.status,
                "time-created": p_request.created_at.isoformat(),
            },
            201,
            {"Location": f"/drives/{p_request.ride_id}/passenger-requests/{p_request.user_id}"},
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
                "id": p_request.user_id,
                "username": p_request.passenger.username,
                "status": p_request.status,
                "time-created": p_request.created_at.isoformat(),
                "time-updated": p_request.last_modified.isoformat(),
            },
            200,
        )
    else:
        abort(401, "Invalid authorization")


@bp.route("/drives/search", methods=["GET"])
def search_drive():
    MIN_RIDES = 1
    MAX_RIDES = 25
    try:
        limit = request.args.get("limit")
        start = request.args.get("from")
        start_distance = request.args.get("from-distance")
        stop = request.args.get("to")
        stop_distance = request.args.get("to-distance")
        arrive_by = request.args.get("arrive-by")
        arrival_delta = request.args.get("arrival-delta")
        depart_by = request.args.get("depart-by")
        depart_delta = request.args.get("depart-delta")
        sex = request.args.get("sex")
    except KeyError:
        abort(400, "Invalid format")

    if limit:
        limit = max(MIN_RIDES, min(int(limit), MAX_RIDES))
    if start:
        start = map(float, start.split(","))
        start_distance = int(start_distance) if start_distance else 5000
    if stop:
        stop = map(float, stop.split(","))
        stop_distance = int(stop_distance) if stop_distance else 5000
    if depart_by:
        depart_by = datetime.strptime(depart_by, "%Y-%m-%dT%H:%M:%S.%f")
        depart_delta = timedelta(minutes=int(depart_delta)) if depart_delta else timedelta(minutes=30)
    if arrive_by:
        arrive_by = datetime.strptime(arrive_by, "%Y-%m-%dT%H:%M:%S.%f")
        arrival_delta = timedelta(minutes=int(arrival_delta)) if arrival_delta else timedelta(minutes=30)

    rides = search_drives(limit, start, start_distance, stop, stop_distance, depart_by,
                          depart_delta, arrive_by, arrival_delta, sex, age_range=None,
                          consumption_range=None)
    return Response(
        json.dumps([
            {
                "id": ride.id,
                "driver-id": ride.driver_id,
                "passenger-ids": [req.user_id for req in ride.accepted_requests()],
                "from": ride.depart_from,
                "to": ride.arrive_at,
                "arrive-by": ride.arrival_time.isoformat(),
            } for ride in rides
        ]),
        status=200,
        mimetype="application/json"
    )
