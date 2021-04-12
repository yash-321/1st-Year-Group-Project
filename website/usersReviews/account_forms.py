from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from website.models import User

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=5, max=15)], render_kw={"placeholder": "Min 5 characters"})

	display_name = StringField('Display Name', validators=[DataRequired(), Length(min=3, max=15)], render_kw={"placeholder": "Min 3 characters"})

	password= PasswordField('Password', validators=[DataRequired(), Length(min=7, max=30)], render_kw={"placeholder": "Min 7 characters"})

	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

	agree= BooleanField('I agree to the terms & conditions', validators=[DataRequired()])

	question_1 = StringField('What is your oldest siblings name?', validators=[DataRequired()])

	question_2 = StringField('What is your first pets name?', validators=[DataRequired()])

	question_3 = StringField('What is your favourite food?', validators=[DataRequired()])

	submit_register = SubmitField('Register', validators=[DataRequired()])

	def validate_username(self, username):

		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken, please choose a different one.')


class LoginForm(FlaskForm):

	username = StringField('Username', validators=[DataRequired()])

	password= PasswordField('Password', validators=[DataRequired()])

	remember= BooleanField('Remember Me')

	submit_login = SubmitField('Log In')

class ForgotPasswordForm(FlaskForm):

	username = StringField('Username', validators=[DataRequired()])

	question_1 = StringField('What is your oldest siblings name?', validators=[DataRequired()])

	question_2 = StringField('What is your first pets name?', validators=[DataRequired()])

	question_3 = StringField('What is your favourite food?', validators=[DataRequired()])

	password= PasswordField('New Password', validators=[DataRequired()])

	submit_forgot_password = SubmitField('Confirm Changes', validators=[DataRequired()])

class UpdateQuestionsForm(FlaskForm):

	question_1 = StringField('What is your oldest siblings name?', validators=[DataRequired()])

	question_2 = StringField('What is your first pets name?', validators=[DataRequired()])

	question_3 = StringField('What is your favourite food?', validators=[DataRequired()])

	submit_change_q = SubmitField('Submit Changes', validators=[DataRequired()]) 

class UpdatePasswordForm(FlaskForm):

	new_password= PasswordField('Enter your new password', validators=[DataRequired()])

	confirm_new_password = PasswordField('Confirm your new password', validators=[DataRequired(), EqualTo('new_password')])

	submit_change_p = SubmitField('Submit Changes', validators=[DataRequired()])

class UpdateNameForm(FlaskForm):

	new_display_name = StringField('Enter your new display name', validators=[DataRequired()])

	submit_change_n = SubmitField('Submit Changes', validators=[DataRequired()])

class ReviewForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	content = TextAreaField('Content', validators=[DataRequired()])
	submit_review = SubmitField('Publish')
