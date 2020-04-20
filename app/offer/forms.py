from wtforms import SubmitField
from wtforms.fields import IntegerField, HiddenField, SelectField, FloatField, StringField, TimeField, DateField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Optional
from app.forms import DictForm
import dateutil.parser
from datetime import datetime
from app.models import Ride
from app.crud import read_car_from_plate


class OfferForm(DictForm):
    from_lat = FloatField('', [NumberRange(-90, 90)])
    from_lon = FloatField('', [NumberRange(-180, 180)])
    to_lat = FloatField('', [NumberRange(-90, 90)])
    to_lon = FloatField('', [NumberRange(-180, 180)])

    arrival_id = StringField('')
    departure_id = StringField('')

    time = TimeField('arrival time', [DataRequired()])
    date = DateField('arrival date', [DataRequired()])

    arrival_time = HiddenField('Arrival Time*', [DataRequired()])
    departure_time = HiddenField('Departure Time')

    passenger_places = IntegerField('Number of Passengers*', [NumberRange(1)])
    car_string = SelectField('Select Car', choices=[('None', 'None')])
    confirm = SubmitField('Confirm')

    def from_database(self, ride: Ride):
        self.from_lat.data = ride.depart_from[0]
        self.from_lon.data = ride.depart_from[1]
        self.to_lat.data = ride.arrive_at[0]
        self.to_lon.data = ride.arrive_at[1]
        self.arrival_id.data = ride.arrival_id
        self.departure_id.data = ride.departure_id
        if ride.departure_time:
            self.departure_time.data = ride.departure_time
        self.arrival_time.data = ride.arrival_time
        self.passenger_places.data = ride.passenger_places
        if ride.car is not None:
            self.car_string.data = ride.car.license_plate
        else:
            self.car_string.data = 'None'

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
            self.arrival_time.data = dateutil.parser.isoparse(arrival_time.data).replace(tzinfo=None)
        except:
            raise ValidationError('Not a valid date format')
        if arrival_time.data <= datetime.utcnow():
            raise ValidationError('Arrival time must be in the future')

    def validate_departure_time(self, departure_time):
        if not departure_time.data:
            departure_time.data = None
            return
        try:
            self.departure_time.data = dateutil.parser.isoparse(departure_time.data).replace(tzinfo=None)
        except:
            raise ValidationError('Not a valid date format')
        if departure_time.data <= datetime.utcnow():
            raise ValidationError('Departure time must be in the future')
        if departure_time.data >= self.arrival_time.data:
            raise ValidationError('Departure time must be before arrival time')

    def validate_car_string(self, car_string):
        if not car_string.data:
            car_string.data = None
            return
        car = read_car_from_plate(car_string.data)
        if not car:
            raise ValidationError('Car does not exist')
        if car.passenger_places < self.passenger_places.data:
            raise ValidationError('Car has not enough passenger places for this ride')


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
    edit = SubmitField('edit offer')
    delete = SubmitField('delete offer')


class DeleteRequestForm(DictForm):
    ride_id = IntegerField('ride_id', [DataRequired()])
    delete = SubmitField('delete request')
