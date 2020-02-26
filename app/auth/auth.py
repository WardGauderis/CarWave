from flask_login import current_user, login_required, login_user
from flask_httpauth import HTTPTokenAuth
from app.models import User
from app.errors.errors import api_error
from functools import wraps
from flask import g

token_auth = HTTPTokenAuth('Bearer')


@token_auth.verify_token
def verify_token(token):
    user = User.from_token(token)
    if user is None:
        return False
    g.current_user = user
    return True


@token_auth.error_handler
def token_error_handler():
    return api_error(401, 'Invalid authorization')
