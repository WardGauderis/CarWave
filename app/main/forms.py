from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields import TimeField, DateField
from wtforms.validators import DataRequired


class DriveForm(FlaskForm):
    from_location = StringField('', [DataRequired()])
    to_location = StringField('', [DataRequired()])
    time = TimeField('', [DataRequired()])
    date = DateField('', [DataRequired()])
    offer = SubmitField('offer')
    find = SubmitField('find')

