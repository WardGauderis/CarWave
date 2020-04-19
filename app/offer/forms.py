from wtforms import SubmitField
from wtforms.fields import IntegerField, HiddenField, SelectField, FloatField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from app.forms import DictForm
import dateutil.parser
import pytz
from datetime import datetime, timezone


class OfferForm(DictForm):
    from_lon = FloatField('', [NumberRange(-180, 180)])
    from_lat = FloatField('', [NumberRange(-90, 90)])
    to_lon = FloatField('', [NumberRange(-180, 180)])
    to_lat = FloatField('', [NumberRange(-90, 90)])

    # from_lon = HiddenField('')
    # from_lat = HiddenField('')
    # to_lon = HiddenField('')
    # to_lat = HiddenField('')

    arrival_time = HiddenField('Arrival Time*', [DataRequired()])
    passenger_places = IntegerField('Number of Passengers*', [NumberRange(1)])
    car_string = SelectField('Select Car', choices=[('None', 'None')])
    confirm = SubmitField('Confirm')

    def from_json(self, json):
        self.arrival_time.data = json.get('arrive-by')
        try:
            self.passenger_places.process_formdata([json.get('passenger-places', 0)])
        except Exception as e:
            self.all_errors['passenger_places'] = str(e)
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
            self.arrival_time.data = dateutil.parser.isoparse(arrival_time.data)
        except:
            raise ValidationError('Not a valid date format')
        if arrival_time.data <= datetime.utcnow():
            raise ValidationError('Arrival time must be in the future')


class FilterForm(DictForm):
    gender = SelectField('select gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    age = IntegerField('age', [NumberRange(min=11, max=125, message='age must be between 12 and 125')])
    usage = IntegerField('usage')
    refresh = SubmitField('refresh')


class RequestChoiceForm(DictForm):
    ride_id = IntegerField('ride_id', [DataRequired()])
    reject = SubmitField('reject passenger')
    accept = SubmitField('accept passenger')


class SelectForm(DictForm):
    ride_id = IntegerField('ride_id', [DataRequired()])
    request = SubmitField('request')


class DeleteOfferForm(DictForm):
    ride_id = IntegerField('ride_id', [DataRequired()])
    delete = SubmitField('delete offer')


class DeleteRequestForm(DictForm):
    ride_id = IntegerField('ride_id', [DataRequired()])
    delete = SubmitField('delete request')
