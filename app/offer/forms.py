from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields import IntegerField, FloatField, StringField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from app.forms import DictForm
from datetime import datetime
import dateutil.parser


class OfferForm(DictForm):
    from_lon = FloatField('', [DataRequired(), NumberRange(-180, 180)])
    from_lat = FloatField('', [DataRequired(), NumberRange(-90, 90)])
    to_lon = FloatField('', [DataRequired(), NumberRange(-180, 180)])
    to_lat = FloatField('', [DataRequired(), NumberRange(-90, 90)])

    arrival_time = StringField('arrival time', [DataRequired()])
    passenger_places = IntegerField('number of passengers', [DataRequired(), NumberRange(1)])
    confirm = SubmitField('confirm')

    def from_json(self, json):
        self.arrival_time.data = json.get('arrive-by')
        self.passenger_places.process_formdata([json.get('passenger-places', 0)])
        try:
            self.from_lat.data = float(json.get('from')[0])
            self.from_lon.data = float(json.get('from')[1])
        except:
            self.all_errors['from'] = "Not a valid coordinate type"
        try:
            self.to_lat.data = float(json.get('to')[0])
            self.to_lon.data = float(json.get('to')[1])
        except:
            self.all_errors['to'] = "Not a valid coordinate type"
        return self.validate_json()

    def validate_arrival_time(self, arrival_time):
        try:
            arrival_time.data = dateutil.parser.isoparse(arrival_time.data)
        except:
            self.all_errors['arrive-by'] = "Not a valid date format"
            return

        if arrival_time.data <= datetime.utcnow():
            raise ValidationError('Arrival time must be in the future')


class FindForm(FlaskForm):
    ride_id = IntegerField('ride_id', [DataRequired()])
    request = SubmitField('request')
