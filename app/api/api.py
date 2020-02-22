from flask import request
from app.api import bp


@bp.route('/users/register', methods=['POST'])
def register_user():
    username = request.form['username']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    password = request.form['password']

    id = 0
    return {'id': id}, 201


@bp.route('/users/auth', methods=['POST'])
def authorize_user():
    username = request.form['username']
    password = request.form['password']

    accepted = True
    if accepted:
        token = ''
        return {'token': token}, 200
    else:
        return 401


@bp.route('/drives', methods=['POST'])
def register_drive():
    token = request.headers['Authorization']

    start = request.form['from']
    stop = request.form['to']
    passenger_places = request.form['passenger-places']
    arrive_by = request.form['arrive-by']

    accepted = True
    if accepted:
        id = 0
        driver_id = 0
        passenger_ids = []
        return {'id': id, 'driver-id': driver_id, 'passenger-ids': passenger_ids, 'passenger-places': passenger_places,
                'from': start, 'to': stop, 'arrive-by': arrive_by}, 201
    else:
        return 401


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
def get_passenger_requests(drive_id):
    token = request.headers['Authorization']

    if request.method == 'GET':
        accepted = True
        if accepted:
            id = 0
            username = ''
            status = ''
            time_created = ''
            return [{'id': id, 'username': username, 'status': status, 'time-created': time_created}], 200
        else:
            return 401
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
            return 401


@bp.route('/drives/<int:drive_id>/passenger-requests/<int:user_id>', methods=['POST'])
def accept_passenger_request(drive_id, user_id):
    token = request.headers['Authorization']

    accepted = True
    if accepted:
        action = request.form['action']

        id = 0
        username = ''
        status = ''
        time_created = ''
        time_updated = ''
        return {'id': id, 'username': username, 'status': status, 'time-created': time_created,
                'time-updated': time_updated}, 200
    else:
        return 401


@bp.route('/drives/search', methods=['GET'])
def search_drive():
    limit = request.args.get('limit')

    start = request.form['from']
    stop = request.form['to']
    arrive_by = request.form['arrive-by']

    id = 0
    driver_id = 0
    passenger_ids = []
    return [{'id': id, 'driver-id': driver_id, 'passenger-ids': passenger_ids, 'from': start, 'to': stop,
             'arrive-by': arrive_by}], 200
