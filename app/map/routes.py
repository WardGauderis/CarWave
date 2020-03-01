from flask import render_template
from app.map import bp
from app.map.forms import WaypointsForm

@bp.route('/map')
def map():
    form = WaypointsForm()
    return render_template('map.html', title='Map', form=form)
