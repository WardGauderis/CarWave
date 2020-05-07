from flask import Blueprint

bp = Blueprint('review', __name__, static_folder='static', template_folder='templates',
               static_url_path='/static/review')

from app.review import review
