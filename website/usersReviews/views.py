from flask import Blueprint, render_template, url_for, flash, redirect, session
from flask_login import login_user, current_user, logout_user, login_required
from website.usersReviews.account_forms import RegistrationForm, LoginForm, ForgotPasswordForm, UpdateQuestionsForm, UpdatePasswordForm
from website import db, bcrypt
from website.models import User
import requests

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


@usersReviews.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	questions_form = UpdateQuestionsForm()
	password_form = UpdatePasswordForm()

	user = User.query.filter_by(username=current_user.username).first()

	if questions_form.validate_on_submit():
		if user and bcrypt.check_password_hash(user.password, questions_form.password.data):
			user.question_1 = form.question_1.data
			user.question_2 = form.question_2.data
			user.question_3 = form.question_3.data
			db.session.commit()
			flash(f'Your security questions has been updated!', 'success')
			return redirect(url_for('usersReviews.account'))
		else:
			flash(f'Password is wrong, check again', 'danger')
	elif password_form.validate_on_submit():
		if user and bcrypt.check_password_hash(user.password, password_form.old_password):
			new_hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
			user.password = new_hashed_password
			db.session.commit()
			flash(f'Your password has been succesfully updated!', 'success')
			return redirect(url_for('usersReviews.account'))
		else:
			flash(f'Password is wrong, check again', 'danger')
	return render_template('account.html', title='Account', form1=questions_form, form2=password_form)



#reviews routes
@usersReviews.route("/writeReview/<movie_id>")
def writeReviews(movie_id):
	return render_template('writeReview.html', title='Write A Review')


@usersReviews.route("/detailedReview/ID=<movie_id>")
def detailed_review(movie_id):
	# query the API to get the data about a specific movie
	respString = 'http://www.omdbapi.com/?i=' + movie_id + '&apikey=b3814b2&plot=full'
	r = requests.get(respString) #, timeout=1)
	dictionary = r.json()

	error_message = movie_title = genres = year_of_movie = poster_url = imdb_rating = plot = actors \
	= directors = runtime = language = awards = production = writer = None

	if dictionary["Response"] != "False":
		movie_title = dictionary["Title"]
		genres = dictionary["Genre"]
		year_of_movie = dictionary["Year"]
		poster_url = dictionary["Poster"].strip()
		imdb_rating = dictionary["imdbRating"]
		plot = dictionary["Plot"]
		actors = dictionary["Actors"]
		directors = dictionary["Director"]
		runtime = dictionary["Runtime"]
		language = dictionary["Language"]
		awards = dictionary["Awards"].strip()

		production = dictionary["Production"].strip()
		writer = dictionary["Writer"].strip()
	else:
		error_message = "The movie was not found! Try again!"

	return render_template(
		'detailed_review.html',
		title='Movie Reviews',
		error_message=error_message,
		movie_title=movie_title,
		genres=genres,
		year_of_movie=year_of_movie,
		poster=poster_url,
		imdb_rating=imdb_rating,
		plot=plot,
		actors=actors,
		directors=directors,
		runtime=runtime,
		language=language,
		awards=awards,
		production=production,
		writer=writer)
