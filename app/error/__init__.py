from flask import Blueprint

bp = Blueprint('error', __name__, template_folder='templates', static_folder='static', static_url_path='/static/map')

from app.error import errors
