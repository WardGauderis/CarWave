from flask import Blueprint

bp = Blueprint('text', __name__, static_folder='static', template_folder='templates')

from app.text import routes