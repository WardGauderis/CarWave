from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
from app.models import User
from app.forms import DictForm


class LoginForm(DictForm):
    username = StringField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def from_json(self, json):
        self.load_json(json)
        return self.validate_json()


class RegistrationForm(DictForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[Optional(), Length(max=128), Email()])
    firstname = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=64)])
    password_validation = PasswordField('Repeat Password', [Optional(), EqualTo('password')])
    submit = SubmitField('Register')

    def from_json(self, json):
        self.load_json(json)
        self.password_validation.process_formdata(self.password.data)
        return self.validate_json()

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username has already been taken.')


class ResetPasswordRequestForm(DictForm):
    email = StringField('Email', validators=[Email(), DataRequired()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(DictForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


class EditProfileForm(DictForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    # email = StringField('Email', validators=[DataRequired(), Length(max=128), Email()])
    # phone_number = StringField('Phone number', validators=[Length(max=64)])
    submit = SubmitField('Save changes')
