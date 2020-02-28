from flask import request, abort
from app.api import bp
from app.auth.auth import token_auth
from app.models import User
from app import db


@bp.route('/users/register', methods=['POST'])
def register_user():
    json = request.get_json() or {}
    try:
        username = json['username']
        first_name = json['firstname']
        last_name = json['lastname']
        password = json['password']
    except KeyError:
        abort(400, 'invalid format')

    user = User(username=username, first_name=first_name, last_name=last_name)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    id = user.id
    return {'id': id}, 201


@bp.route('/users/auth', methods=['POST'])
def authorize_user():
    json = request.get_json() or {}
    try:
        username = json['username']
        password = json['password']
    except KeyError:
        abort(400, 'invalid format')

    user = User.from_username(username)
    if user is not None and user.check_password(password):
        token = user.get_token()
        return {'token': token}, 200
    else:
        abort(401, 'invalid authorization')


@bp.route('/drives', methods=['POST'])
@token_auth.login_required
def register_drive():
    json = request.get_json() or {}
    try:
        start = json['from']
        stop = json['to']
        passenger_places = json['passenger-places']
        arrive_by = json['arrive-by']
    except KeyError:
        abort(400, 'invalid format')

    accepted = True
    if accepted:
        id = 0
        driver_id = 0
        passenger_ids = []
        location = '/drives/{}'.format(0)
        return {'id': id, 'driver-id': driver_id, 'passenger-ids': passenger_ids, 'passenger-places': passenger_places,
                'from': start, 'to': stop, 'arrive-by': arrive_by}, 201, {'Location': location}
    else:
        abort(401, 'invalid authorization')


@bp.route('/drives/<int:drive_id>', methods=['GET'])
def get_drive(drive_id):
    id = 0
    driver_id = 0
    passenger_ids = []
    passenger_places = 0
    start = [0, 0]
    stop = [0, 0]
    arrive_by = ''
    return {'id': id, 'driver-id': driver_id, 'passenger-ids': passenger_ids, 'passenger-places': passenger_places,
            'from': start, 'to': stop, 'arrive-by': arrive_by}, 200


@bp.route('/drives/<int:drive_id>/passengers', methods=['GET'])
def get_passengers(drive_id):
    id = 0
    username = ''
    return [{'id': id, 'username': username}], 200


@bp.route('/drives/<int:drive_id>/passenger-requests', methods=['GET', 'POST'])
@token_auth.login_required
def get_passenger_requests(drive_id):
    if request.method == 'GET':
        accepted = True
        if accepted:
            id = 0
            username = ''
            status = ''
            time_created = ''
            return {'id': id, 'username': username, 'status': status, 'time-created': time_created}, 200
        else:
            abort(401, 'invalid authorization')
    else:
        accepted = True
        if accepted:
            id = 0
            username = ''
            status = ''
            time_created = ''
            location = '/drives/{}/passenger-requests/{}'.format(0, 0)
            return {'id': id, 'username': username, 'status': status, 'time-created': time_created}, 201, {
                'Location': location}
        else:
            abort(401, 'invalid authorization')


@bp.route('/drives/<int:drive_id>/passenger-requests/<int:user_id>', methods=['POST'])
@token_auth.login_required
def accept_passenger_request(drive_id, user_id):
    accepted = True
    if accepted:
        json = request.get_json() or {}
        try:
            action = json['action']
        except KeyError:
            abort(400, 'invalid format')

        id = 0
        username = ''
        status = ''
        time_created = ''
        time_updated = ''
        return {'id': id, 'username': username, 'status': status, 'time-created': time_created,
                'time-updated': time_updated}, 200
    else:
        abort(401, 'invalid authorization')


@bp.route('/drives/search', methods=['GET'])
def search_drive():
    json = request.get_json() or {}
    try:
        limit = request.args['limit']
        start = json['from']
        stop = json['to']
        arrive_by = json['arrive-by']
    except KeyError:
        abort(400, 'invalid format')

    id = 0
    driver_id = 0
    passenger_ids = []
    return [{'id': id, 'driver-id': driver_id, 'passenger-ids': passenger_ids, 'from': start, 'to': stop,
             'arrive-by': arrive_by}], 200
