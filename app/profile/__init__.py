from flask import Blueprint

bp = Blueprint('profile', __name__, static_folder='static', template_folder='templates')

from app.profile import profile
