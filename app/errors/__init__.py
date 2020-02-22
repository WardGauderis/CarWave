from flask import Blueprint

bp = Blueprint('errors', __name__, static_folder='static', template_folder='templates')

from app.errors import errors
