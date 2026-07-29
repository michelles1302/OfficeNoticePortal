from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    """Form used for authentication logging."""
    email = StringField('Email Address', validators=[
        DataRequired(message="Email address is required."),
        Email(message="Please enter a valid email address."),
        Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required.")
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class ProfileForm(FlaskForm):
    """Form used to update basic profile information (excluding roles)."""
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=2, max=80, message="Username must be between 2 and 80 characters.")
    ])
    email = StringField('Email Address', validators=[
        DataRequired(message="Email address is required."),
        Email(message="Please enter a valid email address."),
        Length(max=120)
    ])
    submit = SubmitField('Update Profile')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already taken.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data.lower()).first()
            if user:
                raise ValidationError('Email is already registered.')


class ChangePasswordForm(FlaskForm):
    """Form used to securely change user passwords."""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message="Current password is required.")
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message="New password is required."),
        Length(min=6, max=50, message="New password must be between 6 and 50 characters.")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message="Please confirm your new password."),
        EqualTo('new_password', message="Passwords must match.")
    ])
    submit = SubmitField('Change Password')
