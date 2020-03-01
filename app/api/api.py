from flask import abort, request

from app import db
from app.api import bp
from app.auth.auth import token_auth
from app.models import Car, Driver, Passenger, Ride, User


@bp.route("/users/register", methods=["POST"])
def register_user():
    json = request.get_json() or {}
    try:
        username = json["username"]
        first_name = json["firstname"]
        last_name = json["lastname"]
        password = json["password"]
    except KeyError:
        abort(400, "invalid format")

    # FIXME(Hayaan/groep): creation of a user with an already existing username?
    id = User.create_user(
        username=username, first_name=first_name, last_name=last_name, password=password
    )
    return {"id": id}, 201


@bp.route("/users/auth", methods=["POST"])
def authorize_user():
    json = request.get_json() or {}
    try:
        username = json["username"]
        password = json["password"]
    except KeyError:
        abort(400, "invalid format")

    user = User.from_username(username)
    if user is not None and user.check_password(password):
        token = user.get_token()
        return {"token": token}, 200
    else:
        abort(401, "invalid authorization")


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
        abort(400, "invalid format")

    accepted = True  # TODO(Ward): condition?
    if accepted:
        # TODO: wie kan rides aanmaken? driver, passenger of beide?
        id = 0
        driver_id = 0
        passenger_ids = []
        location = f"/drives/{0}"
        return (
            {
                "id": id,
                "driver-id": driver_id,
                "passenger-ids": passenger_ids,
                "passenger-places": passenger_places,
                "from": start,
                "to": stop,
                "arrive-by": arrive_by,
            },
            201,
            {"Location": location},
        )
    else:
        abort(401, "invalid authorization")


@bp.route("/drives/<int:drive_id>", methods=["GET"])
def get_drive(drive_id: int):
    ride = Ride.get_ride(drive_id)

    if ride is None:
        abort(400, "invalid drive id")

    return (
        {
            "id": ride.id,
            "driver-id": ride.driver_id,
            "passenger-ids": [
                passenger.id for passenger in ride.passengers
            ],  # FIXME(Hayaan)
            "passenger-places": 0,  # FIXME(Hayaan): test whether it uses repr or str
            "from": 0,
            "start": 0,
            "arrive-by": ride.arrival_time,
        },
        200,
    )
    # id = 0
    # driver_id = 0
    # passenger_ids = []
    # passenger_places = 0
    # start = [0, 0]
    # stop = [0, 0]
    # arrive_by = ""
    # return (
    #     {
    #         "id": id,
    #         "driver-id": driver_id,
    #         "passenger-ids": passenger_ids,
    #         "passenger-places": passenger_places,
    #         "from": start,
    #         "to": stop,
    #         "arrive-by": arrive_by,
    #     },
    #     200,
    # )


@bp.route("/drives/<int:drive_id>/passengers", methods=["GET"])
def get_passengers(drive_id):
    ride = Ride.get_ride(drive_id)

    if ride is None:
        abort(400, "invalid drive id")

    return (
        [passenger.to_json() for passenger in ride.passengers],
        200,
    )


@bp.route("/drives/<int:drive_id>/passenger-requests", methods=["GET", "POST"])
@token_auth.login_required
def get_passenger_requests(drive_id):
    if request.method == "GET":
        accepted = True
        if accepted:
            ride = Ride.get_ride(drive_id)
            return (
                [
                    {
                        "id": passenger.id,
                        "username": passenger.user.username,
                        "status": "pending",  # FIXME(Hayaan)
                        "time-created": passenger.user.created_at,
                    }
                    for passenger in ride.passengers
                ],
                200,
            )
        else:
            abort(401, "invalid authorization")
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
            abort(401, "invalid authorization")


@bp.route("/drives/<int:drive_id>/passenger-requests/<int:user_id>", methods=["POST"])
@token_auth.login_required
def accept_passenger_request(drive_id, user_id):
    accepted = True
    if accepted:
        json = request.get_json() or {}
        try:
            action = json["action"]
        except KeyError:
            abort(400, "invalid format")

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
        abort(401, "invalid authorization")


@bp.route("/drives/search", methods=["GET"])
def search_drive():
    json = request.get_json() or {}
    try:
        limit = request.args["limit"]
        start = json["from"]
        stop = json["to"]
        arrive_by = json["arrive-by"]
    except KeyError:
        abort(400, "invalid format")

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
