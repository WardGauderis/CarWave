from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields import TimeField, DateField
from wtforms.validators import DataRequired, ValidationError
from datetime import datetime
import dateutil.parser
import pytz


class DriveForm(FlaskForm):
    from_location = StringField('', [DataRequired()])
    to_location = StringField('', [DataRequired()])
    time = TimeField('', [DataRequired()])
    date = DateField('', [DataRequired()])
    offer = SubmitField('offer')
    find = SubmitField('find')

    def validate_depart_time(self, time):
        if dateutil.parser.isoparse(time.data) <= pytz.utc.localize(datetime.utcnow()):
            raise ValidationError('Arrival time must be in the future')

