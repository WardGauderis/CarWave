from flask import Blueprint

bp = Blueprint('review', __name__, static_folder='static', template_folder='templates')

from app.review import review
