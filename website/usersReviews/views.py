from flask import Blueprint, render_template, url_for, flash, redirect, session, request
from flask_login import login_user, current_user, logout_user, login_required
from website.usersReviews.account_forms import RegistrationForm, LoginForm, ForgotPasswordForm, UpdateQuestionsForm, UpdatePasswordForm, UpdateNameForm, ReviewForm
from website import db, bcrypt
from website.models import User, Whitelist, Blacklist, Review
import requests
from sqlalchemy import exc

usersReviews = Blueprint('usersReviews', __name__)


#users routes
@usersReviews.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('misc.home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		try:
			hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
			hq_1 = bcrypt.generate_password_hash(form.question_1.data).decode('utf-8')
			hq_2 = bcrypt.generate_password_hash(form.question_2.data).decode('utf-8')
			hq_3 = bcrypt.generate_password_hash(form.question_3.data).decode('utf-8')
			user = User(username= form.username.data, display_name=form.display_name.data, password=hashed_password,
						question_1 = hq_1, question_2 = hq_2, question_3 = hq_3)
			db.session.add(user)
			db.session.commit()
			flash(f'Your account has been created! You are able to login now.', 'success')
			return redirect(url_for('usersReviews.login'))
		except exc.IntegrityError:
			flash(f'Username exists, please choose a different one!', 'danger')
			# return redirect(url_for('usersReviews.register'))
			return redirect(url_for('usersReviews.register'))
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
			if 'movieID' in session:
				return redirect(url_for('usersReviews.detailed_review', movie_id=session['movieID']))
			return redirect(url_for('misc.home'))
		else:
			flash(f'Login Unsuccessful. Please check username and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@usersReviews.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
	form = ForgotPasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user and bcrypt.check_password_hash(user.question_1, form.question_1.data) and bcrypt.check_password_hash(user.question_2, form.question_2.data) and bcrypt.check_password_hash(user.question_3, form.question_3.data):
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
	reviews = Review.query.filter_by(user_id=current_user.username).all()
	questions_form = UpdateQuestionsForm()
	password_form = UpdatePasswordForm()
	name_form = UpdateNameForm()

	user = User.query.filter_by(username=current_user.username).first()

	if questions_form.validate_on_submit():
		if user:
			hq_1 = bcrypt.generate_password_hash(questions_form.question_1.data).decode('utf-8')
			hq_2 = bcrypt.generate_password_hash(questions_form.question_2.data).decode('utf-8')
			hq_3 = bcrypt.generate_password_hash(questions_form.question_3.data).decode('utf-8')
			user.question_1 = hq_1
			user.question_2 = hq_2
			user.question_3 = hq_3
			db.session.commit()
			flash(f'Your security questions has been updated!', 'success')
			return redirect(url_for('usersReviews.account'))
		else:
			flash(f'Password is wrong, check again', 'danger')
	elif password_form.validate_on_submit():
		if user:
			new_hashed_password = bcrypt.generate_password_hash(password_form.new_password.data).decode('utf-8')
			user.password = new_hashed_password
			db.session.commit()
			flash(f'Your password has been succesfully updated!', 'success')
			return redirect(url_for('usersReviews.account'))
		else:
			flash(f'Password format is incorrect, check again', 'danger')
	elif name_form.validate_on_submit():
		if user:
			user.display_name = name_form.new_display_name.data
			db.session.commit()
			flash(f'Your display name has been succesfully updated!', 'success')
			return redirect(url_for('usersReviews.account'))
		else:
			flash(f'Display name format is incorrect!', 'danger')

	whitelist = Whitelist.query.filter_by(user_id=user.id).all()
	blacklist = Blacklist.query.filter_by(user_id=user.id).all()

	return render_template(
		'account.html',
		title='Account',
		form1=questions_form,
		form2=password_form,
		form3=name_form,
		whitelist=whitelist,
		blacklist=blacklist,
		reviews=reviews)

@usersReviews.route("/account/<int:review_id>/delete", methods=['POST'])
@login_required
def delete_review(review_id):
	review = Review.query.get_or_404(review_id)
	db.session.delete(review)
	db.session.commit()
	flash('Your review has been deleted!', 'success')
	return redirect(url_for('usersReviews.account'))


@usersReviews.route("/removeMovie", methods=['GET', 'POST'])
def removeMovie():
	data = request.form.to_dict()
	user = User.query.filter_by(username=current_user.username).first()

	if data['buttonpressed'] == "whitelist":
		movie = Whitelist.query.filter_by(movie_id=data['currentMovieID'], user_id=user.id).first()
		db.session.delete(movie)
		db.session.commit()
	elif data['buttonpressed'] == "blacklist":
		movie = Blacklist.query.filter_by(movie_id=data['currentMovieID'], user_id=user.id).first()
		db.session.delete(movie)
		db.session.commit()
	return redirect(url_for('usersReviews.account'))



#reviews routes
@usersReviews.route("/writeReview/<int:review_id>", methods=['GET', 'POST'])
@login_required
def writeReview(review_id):
	review = Review.query.get_or_404(review_id)
	form = ReviewForm()
	if form.validate_on_submit() and (current_user.username == review.user_id):
		review.title = form.title.data
		review.data = form.content.data
		db.session.commit()
		flash('Your review has been updated!', 'success')
		return redirect(url_for('usersReviews.account', review_id=review_id))
	elif request.method == 'GET' and current_user.username == review.user_id:
		form.title.data = review.title
		form.content.data = review.data
	else:
		flash('Unauthorized access', 'danger')
		return redirect(url_for('misc.home'))
	return render_template('writeReview.html', title='Update Review', form=form)


@usersReviews.route("/detailedReview/ID=<movie_id>", methods=['GET', 'POST'])
def detailed_review(movie_id):
	reviews = Review.query.filter_by(movie_id=movie_id).all()

	session.pop('movieID', None)
	# query the API to get the data about a specific movie
	respString = 'http://www.omdbapi.com/?i=' + movie_id + '&apikey=b3814b2&plot=full'
	r = requests.get(respString) #, timeout=1)
	dictionary = r.json()

	error_message = movie_title = genres = year_of_movie = poster_url = imdb_rating = plot = actors \
	= directors = runtime = language = awards = production = writer = None

	if dictionary["Response"] != "False":
		try:
			movie_title = dictionary["Title"]
		except KeyError:
			movie_title = None
		try:
			genres = dictionary["Genre"]
		except KeyError:
			genres = None
		try:
			year_of_movie = dictionary["Year"]
		except KeyError:
			year_of_movie = None
		try:
			movie_title = dictionary["Title"]
		except KeyError:
			movie_title = None
		try:
			poster_url = dictionary["Poster"].strip()
		except KeyError:
			poster_url = None
		try:
			imdb_rating = dictionary["imdbRating"]
		except KeyError:
			imdb_rating = None
		try:
			plot = dictionary["Plot"]
		except KeyError:
			plot = None
		try:
			actors = dictionary["Actors"]
		except KeyError:
			actors = None
		try:
			directors = dictionary["Director"]
		except KeyError:
			directors = None
		try:
			runtime = dictionary["Runtime"]
		except KeyError:
			runtime = None
		try:
			directors = dictionary["Director"]
		except KeyError:
			directors = None
		try:
			language = dictionary["Language"]
		except KeyError:
			language = None
		try:
			awards = dictionary["Awards"].strip()
		except KeyError:
			awards = None
		try:
			production = dictionary["Production"].strip()
		except KeyError:
			production = None
		try:
			writer = dictionary["Writer"].strip()
		except KeyError:
			writer = None
	else:
		error_message = "The movie was not found! Try again!"
		return render_template('errors/404.html'), 404


	#code for reviews

	form = ReviewForm()
	if current_user.is_authenticated:
		author = current_user.username
		display = current_user.display_name
	else:
		author = "Guest"
		display = 'Guest'

	if form.validate_on_submit():
		review = Review(title=form.title.data, data=form.content.data, rating=movie_title, user_id=author, movie_id=movie_id)
		db.session.add(review)
		db.session.commit()
		flash('Your review has been created!', 'success')
		return redirect(f'/detailedReview/ID={movie_id}')

	if current_user.is_authenticated:
		user = User.query.filter_by(username=current_user.username).first()
		if user:
			white = Whitelist.query.filter_by(movie_id=movie_id, user_id=user.id).first()
			if white:
				whitebtn = "red"
			else:
				whitebtn = "white"
			black = Blacklist.query.filter_by(movie_id=movie_id, user_id=user.id).first()
			if black:
				blackbtn = "black"
			else:
				blackbtn = "white"
	else:
		whitebtn = "white"
		blackbtn = "white"



	return render_template(
		'detailed_review.html',
		title='Movie Reviews',
		error_message=error_message,
		movie_id=movie_id,
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
		writer=writer,
		form=form,
		reviews=reviews,
		whitebtn=whitebtn,
		blackbtn=blackbtn)
