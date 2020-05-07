from flask import Blueprint

bp = Blueprint('messages', __name__, static_folder='static', template_folder='templates')

from app.messages import routes