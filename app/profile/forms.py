from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, EqualTo, Email, ValidationError
from app.forms import DictForm
from app.models import User
from flask_login import current_user


class UpdateUserForm(DictForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[Optional(), Length(max=128), Email()])
    firstname = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    submit = SubmitField('Update')

    def from_database(self, user: User):
        self.username.data = user.username
        self.email.data = user.email
        self.firstname.data = user.firstname
        self.lastname.data = user.lastname

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None and user != current_user:
            raise ValidationError('This username has already been taken.')
