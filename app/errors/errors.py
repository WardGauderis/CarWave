from flask import jsonify, request
from werkzeug.http import HTTP_STATUS_CODES
from app.errors import bp


def json_error():
    return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']


def api_error(status_code, description=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if description:
        payload['description'] = description
    response = jsonify(payload)
    response.status_code = status_code
    return response


@bp.app_errorhandler(400)
@bp.app_errorhandler(401)
@bp.app_errorhandler(404)
@bp.app_errorhandler(405)
@bp.app_errorhandler(500)
def not_found(error):
    if json_error():
        return api_error(error.code, error.description)
    else:
        return "DiT iS eEn MoOie ErOr PaGiNa VoOr ErRoR {}: {}<br>{}".format(
            error.code, HTTP_STATUS_CODES.get(error.code, 'Unknown error'), error.description), error.code
