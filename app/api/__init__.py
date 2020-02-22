from flask import Blueprint

bp = Blueprint('api', __name__, static_folder='static', template_folder='templates')

from app.api import api
