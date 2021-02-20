from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from website.models import User

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=3, max=15)])

	display_name = StringField('Display Name', validators=[DataRequired(), Length(min=3, max=15)])

	password= PasswordField('Password', validators=[DataRequired()])

	agree= BooleanField('I agree to the terms & conditions', validators=[DataRequired()])

	submit_register = SubmitField('Register', validators=[DataRequired()]) 

	def validate_username(self, username):

		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken, please choose a different one.')

	def validate_email(self, email):

		user = User.query.filter_by(display_name=display_name.data).first()
		if user:
			raise ValidationError('The email is taken, please choose a different one.')

class LoginForm(FlaskForm):

	username = StringField('Username', validators=[DataRequired()])

	password= PasswordField('Password', validators=[DataRequired()])

	remember= BooleanField('Remember Me')

	submit_login = SubmitField('Log In')
