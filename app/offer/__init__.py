from flask import Blueprint

bp = Blueprint('offer', __name__, static_folder='static', template_folder='templates', static_url_path='/static/offer')

from app.offer import routes