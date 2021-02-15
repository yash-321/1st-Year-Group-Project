import secrets
import os
from flask import render_template, url_for, flash, redirect, request, abort, session
from flask_login import login_user, current_user, logout_user, login_required
from website.account_forms import RegistrationForm, LoginForm
from website import app, db, bcrypt
from website.models import User
import random 
import requests
from datetime import datetime, timedelta

# the period of how long data is saved on the website
app.secret_key = "df78sf845s65fsf9sd5f2fg13513sdfsa"
app.permanent_session_lifetime = timedelta(minutes=10)


@app.route("/")
@app.route("/home")
def home():
	return render_template('base.html', title='Home')
	#this should render index.html but since the inheritence isn't set up on it, using base.html instead.
	#return render_template('index.html', title='Home')


@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form= LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			return redirect(url_for('home'))
		else:
			flash('Login Unsuccesful. Please check username and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username= form.username.data, display_name=form.display_name.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are able to login now.', 'success')
		return redirect(url_for('home'))
	return render_template('register.html', title='Register', form=form)


@app.route("/SearchMovies")
def seeMovieReview():
	return render_template('seeMovieReview.html', title='Search Movies')


@app.route("/writeReview")
def writeReviews():
	return render_template('writeReview.html', title='Write A Review')


@app.route("/detailedReview")
def detailed_review():
	return render_template('detailed_review.html', title='Movie Reviews')


@app.route("/account")
def account():
	return render_template('account.html', title='Account')


@app.route("/suggestMeMovies", methods=['GET', 'POST'])
def suggestMeMovies():
	names_of_genres = ("Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", 
						"Documentary", "Drama", "Family", "Fantasy", "History", "Horror", 
						 "Mystery", "Romance", "Sci-Fi", "Thriller"
						)

	indices_of_checked_genres = []
	number_of_different_genres = len(names_of_genres)
	checked_genres = [""]*number_of_different_genres

	ratings = (0, 7.5, 7, 6.5, 6, 5.5, 5)
	ratings_texts = ("Any Ratings", "Rated over 7.5", "Rated over 7",
					"Rated over 6.5","Rated over 6","Rated over 5.5",
					"Rated over 5")
	chosen_rating = 0


	ranges_of_years_text = ("All years", "2015 – now", "2010 – 2014", "2005 – 2009",
							"2000 – 2004", "1995 – 1999", "1990 – 1994", "1985 – 1989",
							"1980 - 1984", "Older than 1980")

	ranges_of_years = (0, (2015, 2021), (2010, 2014), (2005, 2009), (2000, 2004), (1995, 1999),
					  (1990, 1994), (1985, 1989), (1980, 1984), 1980)

	indices_of_checked_ranges_of_years = []
	number_of_different_ranges_of_years = len(ranges_of_years_text)
	checked_ranges_of_years = [""]*number_of_different_ranges_of_years


	if request.method == 'POST':
		session.permanent = True

		chosen_rating = float(request.form.get('Ratings'))
		session["chosen_rating"] = chosen_rating

		for i in range(number_of_different_genres):
			if request.form.get(names_of_genres[i]):
				indices_of_checked_genres.append(i)
				checked_genres[i] = "checked"
				session["checked_genres" + str(i)] = "checked"
			else:
				if ("checked_genres" + str(i)) in session:
					session.pop("checked_genres" + str(i), None)

		for i in range(number_of_different_ranges_of_years):
			if request.form.get(ranges_of_years_text[i]):
				indices_of_checked_ranges_of_years.append(i)
				checked_ranges_of_years[i] = "checked"
				session["checked_ranges_of_years" + str(i)] = "checked"
			else:
				if ("checked_ranges_of_years" + str(i)) in session:
					session.pop("checked_ranges_of_years" + str(i), None)


	for i in range(number_of_different_genres):
		if ("checked_genres" + str(i)) in session and checked_genres[i] != "checked":
			checked_genres[i] = "checked"
			indices_of_checked_genres.append(i)

	if "chosen_rating" in session:
		chosen_rating = session["chosen_rating"]
	else:
		chosen_rating = 0

	for i in range(number_of_different_ranges_of_years):
		if ("checked_ranges_of_years" + str(i)) in session and checked_ranges_of_years[i] != "checked":
			checked_ranges_of_years[i] = "checked"
			indices_of_checked_ranges_of_years.append(i)


	return render_template(
		'suggestMeMovies.html', 
		title='Suggest Me a Movie',
		names_of_genres=names_of_genres,
		checked_genres=checked_genres,
		number_of_different_genres=number_of_different_genres,
		ratings=ratings,
		ratings_texts=ratings_texts,
		chosen_rating=chosen_rating,
		number_of_different_ranges_of_years=number_of_different_ranges_of_years,
		ranges_of_years_text=ranges_of_years_text,
		checked_ranges_of_years=checked_ranges_of_years
		# data=data
		)
