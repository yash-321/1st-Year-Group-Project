from flask import Blueprint, render_template, url_for, flash, redirect, session
from flask_login import login_user, current_user, logout_user, login_required
from website.usersReviews.account_forms import RegistrationForm, LoginForm, ForgotPasswordForm
from website import db, bcrypt
from website.models import User

usersReviews = Blueprint('usersReviews', __name__)


#users routes
@usersReviews.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('misc.home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username= form.username.data, display_name=form.display_name.data, password=hashed_password,
					question_1 = form.question_1.data, question_2 = form.question_2.data, question_3 = form.question_3.data)
		db.session.add(user)
		db.session.commit()
		flash(f'Your account has been created! You are able to login now.', 'success')
		return redirect(url_for('usersReviews.login'))
	return render_template('register.html', title='Register', form=form)


@usersReviews.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('misc.home'))
	form= LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			return redirect(url_for('misc.home'))
		else:
			flash(f'Login Unsuccessful. Please check username and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@usersReviews.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
	form = ForgotPasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data, question_1=form.question_1.data, 
									question_2=form.question_2.data, question_3=form.question_3.data).first()
		if user:
			new_hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
			user.password = new_hashed_password
			db.session.commit()
			flash('Your password has been succesfully updated!', 'success')
			return redirect(url_for('usersReviews.login'))
	return render_template('forgot_password.html', form=form)


@usersReviews.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('misc.home'))


@usersReviews.route("/account")
def account():
	return render_template('account.html', title='Account')



#reviews routes
@usersReviews.route("/writeReview")
def writeReviews():
	return render_template('writeReview.html', title='Write A Review')


@usersReviews.route("/detailedReview")
def detailed_review():
	return render_template('detailed_review.html', title='Movie Reviews')
