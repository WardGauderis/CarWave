from wtforms import StringField, SubmitField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange
from app.forms import DictForm
from app.models import Car
from flask_login import current_user


class CreateCarForm(DictForm):
    license_plate = StringField('License Plate', [DataRequired(), Length(max=16)])
    model = StringField('Model', [DataRequired(), Length(max=128)])
    colour = StringField('Colour', [DataRequired(), Length(max=32)])
    passenger_places = IntegerField('Passenger Places', [DataRequired(), NumberRange(1)])
    build_year = IntegerField('Build Year', [DataRequired(), NumberRange(1900, 2020)])
    fuel = SelectField('Fuel Type', choices=[('gasoline', 'gasoline'), ('diesel', 'diesel'), ('electric', 'electric')])
    consumption = FloatField('Fuel Consumption', [DataRequired(), NumberRange(0)])
    submit = SubmitField('Register')
    update = False
    old_car_license_plate = str

    def make_update_form(self):
        self.submit.label.text = 'Update'
        self.update = True

    def validate_license_plate(self, license_plate):
        car = Car.query.filter_by(license_plate=license_plate.data).first()
        if self.update and license_plate.data == self.old_car_license_plate:
            return
        if car is not None:
            raise ValidationError('This car is already in use')

    def from_database(self, car: Car):
        self.license_plate.data = car.license_plate
        self.old_car_license_plate = car.license_plate
        self.model.data = car.model
        self.colour.data = car.colour
        self.passenger_places.data = car.passenger_places
        self.build_year.data = car.build_year
        self.fuel.data = car.fuel
        self.consumption.data = car.consumption
