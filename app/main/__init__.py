from flask import Blueprint

bp = Blueprint('main', __name__, static_folder='static', template_folder='templates')

from app.main import routes