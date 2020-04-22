from flask import jsonify, request, render_template
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES

from app.error import bp


def json_error():
    return (
            request.accept_mimetypes["application/json"]
            >= request.accept_mimetypes["text/html"]
    )


def error_message(status_code):
    return HTTP_STATUS_CODES.get(status_code, "Unknown error");


def api_error(status_code, description=None):
    payload = {"code": status_code, "error": error_message(status_code)}
    if description:
        payload["description"] = description
    response = jsonify(payload)
    response.status_code = status_code
    return response


@bp.app_errorhandler(HTTPException)
def error_handler(error):
    if json_error():
        return api_error(error.code, error.description)
    else:
        return render_template('error.html', error=error, message=error_message(error.code), title='Error')
