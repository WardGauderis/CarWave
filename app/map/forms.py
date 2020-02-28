from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class WaypointsForm(FlaskForm):
    start = StringField('start', [DataRequired()])
    end = StringField('end', [DataRequired()])
