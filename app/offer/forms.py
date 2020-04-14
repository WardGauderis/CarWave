from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields import IntegerField, FloatField
from wtforms.validators import DataRequired


class OfferForm(FlaskForm):
    from_lon = FloatField('', [DataRequired()])
    from_lat = FloatField('', [DataRequired()])
    to_lon = FloatField('', [DataRequired()])
    to_lat = FloatField('', [DataRequired()])

    arrival_time = StringField('arrival time', [DataRequired()])
    passengers = IntegerField('number of passengers', [DataRequired()])
    confirm = SubmitField('confirm')

