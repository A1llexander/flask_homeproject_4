from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators

class RegistrationForm(FlaskForm):
    email = StringField('Email Address', [validators.Length(min=6, max=35),
                                          validators.Email()]
                        )
    password = PasswordField('New Password', [validators.DataRequired(),
                                              validators.EqualTo('confirm', message='Passwords must match'),
                                              validators.Length(min=5, max=35)]
                             )
    confirm = PasswordField('Repeat Password')

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[validators.Length(min=6, max=35), validators.Email()])
    password = PasswordField("Password:", [
        validators.DataRequired(),
        validators.Length(min=5, max=35)
    ])