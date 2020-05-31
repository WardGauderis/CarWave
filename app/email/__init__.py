from flask import Blueprint

bp = Blueprint('email', __name__, static_folder='static', template_folder='templates')

