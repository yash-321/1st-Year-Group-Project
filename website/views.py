import secrets
import os
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from website.account_forms import RegistrationForm, LoginForm
from website import app
from website.models import User


@app.route("/")


@app.route("/base")
def home():
	return render_template('base.html', title='Home')


@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form= LoginForm()
	return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	return render_template('register.html', title='Register', form=form)


@app.route("/index")
def index():
	return render_template('index.html', title='Index')


@app.route("/seeMovieReview")
def seeMovieReview():
	return render_template('seeMovieReview.html', title='Movie Reviews')


@app.route("/writeReviews")
def writeReviews():
	return render_template('writeReview.html', title='Write Reviews')


@app.route("/detailed_review")
def detailed_review():
	return render_template('detailed_review.html', title='Detailed Reviews')


@app.route("/account")
def account():
	return render_template('account.html', title='Detailed Reviews')


@app.route("/suggestMeMovies", methods=['GET', 'POST'])
def suggestMeMovies():
	names_of_genres = ("Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", 
						"Documentary", "Drama", "Family", "Fantasy", "History", "Horror", 
						"Music", "Mystery", "Romance", "Sci-Fi", "Thriller"
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
		chosen_rating = float(request.form.get('Ratings'))

		for i in range(number_of_different_genres):
			if request.form.get(names_of_genres[i]):
				indices_of_checked_genres.append(i)
				checked_genres[i] = "checked"

		for i in range(number_of_different_ranges_of_years):
			if request.form.get(ranges_of_years_text[i]):
				indices_of_checked_ranges_of_years.append(i)
				checked_ranges_of_years[i] = "checked"


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
