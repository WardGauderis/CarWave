from flask import Blueprint

bp = Blueprint('offers', __name__, static_folder='static', template_folder='templates')

from app.offers import routes