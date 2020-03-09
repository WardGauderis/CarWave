from flask import render_template
from app.map import bp

@bp.route('/map')
def map():
    return render_template('map.html', title='Map')
