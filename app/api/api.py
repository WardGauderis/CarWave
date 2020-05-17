import json
from datetime import datetime, timedelta

import dateutil
import pytz
from flask import Response, abort, g, request

from app.api import bp
from app.auth.auth import token_auth
from app.auth.forms import LoginForm, UserForm
from app.crud import (create_drive, create_passenger_request, create_user,
                      read_drive_from_id, read_user_from_login, search_drives,
                      update_passenger_request)
from app.models import PassengerRequest, Ride
from app.offer.forms import OfferForm


def belgian_iso_string(time):
    return (
        pytz.timezone("Europe/Brussels")
        .normalize(pytz.utc.localize(time))
        .replace(tzinfo=None)
        .isoformat()
    )


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
                "arrive-by": belgian_iso_string(drive.arrival_time),
            },
            201,
            {"Location": f"/drives/{drive.id}"},
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
            "passenger-ids": [request.user_id for request in ride.accepted_requests()],
            "passenger-places": ride.passenger_places,
            "from": ride.depart_from,
            "to": ride.arrive_at,
            "arrive-by": belgian_iso_string(ride.arrival_time),
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
            [
                {"id": request.user_id, "username": request.passenger.username}
                for request in ride.accepted_requests()
            ]
        ),
        status=200,
        mimetype="application/json",
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
                json.dumps(
                    [
                        {
                            "id": p_request.user_id,
                            "username": p_request.passenger.username,
                            "status": p_request.status,
                            "time-created": belgian_iso_string(p_request.created_at),
                        }
                        for p_request in ride.requests
                    ]
                ),
                status=200,
                mimetype="application/json",
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
                "time-created": belgian_iso_string(p_request.created_at),
            },
            201,
            {
                "Location": f"/drives/{p_request.ride_id}/passenger-requests/{p_request.user_id}"
            },
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
                "time-created": belgian_iso_string(p_request.created_at),
                "time-updated": belgian_iso_string(p_request.last_modified),
            },
            200,
        )
    else:
        abort(401, "Invalid authorization")


@bp.route("/drives/search", methods=["GET"])
def search_drive():
    MIN_RIDES = 1
    MAX_RIDES = 50

    # Arguments
    limit = request.args.get("limit")
    start = request.args.get("from")
    start_distance = request.args.get("from_distance")
    stop = request.args.get("to")
    stop_distance = request.args.get("to_distance")
    arrive_by = request.args.get("arrive_by")
    arrival_delta = request.args.get("arrival_delta")
    depart_by = request.args.get("depart_by")
    depart_delta = request.args.get("depart_delta")
    sex = request.args.get("sex")
    min_consumption = request.args.get("min_consumption")
    max_consumption = request.args.get("max_consumption")
    min_age = request.args.get("min_age")
    max_age = request.args.get("max_age")
    min_rating = request.args.get("min_rating")
    max_rating = request.args.get("max_rating")
    tags = request.args.get("tags")

    # TODO: explicitly type check arguments
    try:
        if limit:
            limit = max(MIN_RIDES, min(int(limit), MAX_RIDES))
        if start:
            start = [*map(str.strip, start.split(","))]
            start_distance = int(start_distance) if start_distance else 5000
        if stop:
            stop = [*map(str.strip, stop.split(","))]
            stop_distance = int(stop_distance) if stop_distance else 5000
        if depart_by:
            depart_by = dateutil.parser.isoparse(depart_by).replace(tzinfo=None)
            depart_by = pytz.utc.normalize(pytz.timezone('Europe/Brussels').localize(depart_by)).replace(tzinfo=None)
            depart_delta = (
                timedelta(minutes=int(depart_delta))
                if depart_delta
                else timedelta(minutes=30)
            )
        if arrive_by:
            arrive_by = dateutil.parser.isoparse(arrive_by).replace(tzinfo=None)
            arrive_by = pytz.utc.normalize(pytz.timezone('Europe/Brussels').localize(arrive_by)).replace(tzinfo=None)
            arrival_delta = (
                timedelta(minutes=int(arrival_delta))
                if arrival_delta
                else timedelta(minutes=30)
            )
        if min_consumption:
            min_consumption = float(min_consumption)
        if max_consumption:
            max_consumption = float(max_consumption)
        if min_age:
            min_age = int(min_age)
        if max_age:
            max_age = int(max_age)
        if min_rating:
            min_rating = float(min_rating)
        if max_rating:
            max_rating = float(max_rating)
        if tags:
            tags = set(map(str.strip, tags.split(",")))
    except Exception as e:
        print(e)
        abort(400, "Invalid format")

    rides = search_drives(
        limit=limit,
        arrival=stop,
        arrival_distance=stop_distance,
        arrival_time=arrive_by,
        arrival_delta=arrival_delta,
        departure=start,
        departure_distance=start_distance,
        departure_time=depart_by,
        departure_delta=depart_delta,
        sex=sex,
        age_range=(min_age, max_age),
        consumption_range=(min_consumption, max_consumption),
        driver_rating=(min_rating, max_rating),
        tags=tags,
    )
    return Response(
        json.dumps(
            [
                {
                    "id": ride.id,
                    "driver-id": ride.driver_id,
                    "passenger-ids": [req.user_id for req in ride.accepted_requests()],
                    "from": ride.depart_from,
                    "to": ride.arrive_at,
                    "arrive-by": belgian_iso_string(
                        datetime.strptime(
                            ride.arrival_time.isoformat(), "%Y-%m-%dT%H:%M:%S"
                        )
                    ),
                }
                for ride in rides
            ]
        ),
        status=200,
        mimetype="application/json",
    )
