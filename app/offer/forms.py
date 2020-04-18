from wtforms import SubmitField
from wtforms.fields import IntegerField, FloatField, StringField, SelectField
from wtforms.validators import DataRequired, NumberRange
from app.forms import DictForm
import dateutil.parser


class OfferForm(DictForm):
    from_lon = FloatField('', [NumberRange(-180, 180)])
    from_lat = FloatField('', [NumberRange(-90, 90)])
    to_lon = FloatField('', [NumberRange(-180, 180)])
    to_lat = FloatField('', [NumberRange(-90, 90)])

    arrival_time = StringField('arrival time', [DataRequired()])
    passenger_places = IntegerField('number of passengers', [NumberRange(1)])
    car_string = SelectField('select car', [DataRequired()], choices=[('None', 'None')])
    confirm = SubmitField('confirm')

    def from_json(self, json):
        try:
            self.arrival_time.data = dateutil.parser.isoparse(json.get('arrive-by'))
        except:
            self.all_errors['arrive-by'] = "Not a valid date format"
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


class FilterForm(DictForm):
    gender = SelectField('select gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    age = IntegerField('age', [NumberRange(min=11, max=125, message='age must be between 12 and 125')])
    usage = IntegerField('usage')
    refresh = SubmitField('refresh')


class SelectForm(DictForm):
    ride_id = IntegerField('ride_id', [DataRequired()])
    request = SubmitField('request')


class DeleteOfferForm(DictForm):
    ride_id = IntegerField('ride_id', [DataRequired()])
    delete = SubmitField('delete offer')


class DeleteRequestForm(DictForm):
    ride_id = IntegerField('ride_id', [DataRequired()])
    delete = SubmitField('delete request')
