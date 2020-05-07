from wtforms import SubmitField
from wtforms.fields import TextAreaField
from wtforms.validators import DataRequired, Length
from app.forms import DictForm


class MessageForm(DictForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Submit')

