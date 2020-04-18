from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
from app.models import User
from app.forms import DictForm
from flask_login import current_user


class LoginForm(DictForm):
    username = StringField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def from_json(self, json):
        self.load_json(json)
        return self.validate_json()


class CreateUserForm(DictForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[Optional(), Length(max=128), Email()])
    firstname = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=64)])
    password_validation = PasswordField('Repeat Password', [Optional(), EqualTo('password')])
    submit = SubmitField('Register')
    update = False

    def make_update_form(self):
        self.submit.label.text = 'Update'
        self.update = True

    def from_json(self, json):
        self.load_json(json)
        self.password_validation.process_formdata(self.password.data)
        return self.validate_json()

    def from_database(self, user: User):
        self.username.data = user.username
        self.email.data = user.email
        self.firstname.data = user.firstname
        self.lastname.data = user.lastname

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            if self.update and user == current_user:
                return
            raise ValidationError('This username has already been taken.')


class ResetPasswordRequestForm(DictForm):
    email = StringField('Email', validators=[Email(), DataRequired()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(DictForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')
