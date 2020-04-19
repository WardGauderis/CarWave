from wtforms import StringField, SubmitField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange
from app.forms import DictForm
from app.crud import read_car_from_plate


class CreateCarForm(DictForm):
    license_plate = StringField('License Plate*', [DataRequired(), Length(max=16)])
    model = StringField('Model*', [DataRequired(), Length(max=128)])
    colour = StringField('Colour*', [DataRequired(), Length(max=32)])
    passenger_places = IntegerField('Passenger Places*', [NumberRange(1)])
    build_year = IntegerField('Build Year*', [NumberRange(1900, 2020)])
    fuel = SelectField('Fuel Type*', choices=[('gasoline', 'gasoline'), ('diesel', 'diesel'), ('electric', 'electric')])
    consumption = FloatField('Fuel Consumption*', [NumberRange(0)])
    submit = SubmitField('Register Car')
    update = False

    def from_database(self, car):
        self.license_plate.data = car.license_plate
        self.model.data = car.model
        self.colour.data = car.colour
        self.passenger_places.data = car.passenger_places
        self.build_year.data = car.build_year
        self.fuel.data = car.fuel
        self.consumption.data = car.consumption
        self.fuel.data = car.fuel

    def make_update_form(self):
        self.submit.label.text = 'Update Car'
        self.update = True

    def validate_license_plate(self, license_plate):
        if self.update:
            return
        car = read_car_from_plate(license_plate.data)
        if car is not None:
            raise ValidationError('This car is already in use')
