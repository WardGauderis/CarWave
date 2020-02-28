from flask import Blueprint

bp = Blueprint('map', __name__, static_folder='static', template_folder='templates', static_url_path='/static/map')

from app.map import routes
