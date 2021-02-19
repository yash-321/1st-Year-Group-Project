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

# the period of time for how long data is saved on the website
app.secret_key = "df78sf845s65fsf9sd5f2fg13513sdfsa"
app.permanent_session_lifetime = timedelta(minutes=10)


@app.route("/")
@app.route("/home")
def home():
	return render_template('base.html', title='Home')
	#this should render index.html but since the inheritence isn't set up on it, using base.html instead.
	#return render_template('index.html', title='Home')


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
		flash(f'Your account has been created! You are able to login now.', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)


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
			flash(f'Login Unsuccesful. Please check username and password', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

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
	# the tuples and lists to save the required data for criteria

	names_of_genres = ("Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", 
						"Documentary", "Drama", "Family", "Fantasy", "History", "Horror", 
						 "Mystery", "Romance", "Sci-Fi", "Thriller")

	indices_of_checked_genres = []
	number_of_different_genres = len(names_of_genres)
	checked_genres = [""]*number_of_different_genres

	ratings = (0, 7.5, 7, 6.5, 6, 5.5, 5)
	ratings_texts = ("Any Ratings", "Rated over 7.5", "Rated over 7",
					"Rated over 6.5","Rated over 6","Rated over 5.5",
					"Rated over 5")
	chosen_rating = 0
	number_of_different_ratings = len(ratings)

	ranges_of_years_text = ("All years", "2015 – now", "2010 – 2014", "2005 – 2009",
							"2000 – 2004", "1995 – 1999", "1990 – 1994", "1960 – 1989", "Older than 1960")

	ranges_of_years = (0, (2015, 2021), (2010, 2014), (2005, 2009), (2000, 2004), (1995, 1999),
					  (1990, 1994), (1960, 1989), 1960)

	indices_of_checked_ranges_of_years = []
	number_of_different_ranges_of_years = len(ranges_of_years_text)
	checked_ranges_of_years = [""]*number_of_different_ranges_of_years

	# executes when the button "generate the movie" was pressed
	# this code encures that the selected criteria does not reset after every refresh of the page
	if request.method == 'POST':
		# session saves the checked criteria if the page was left
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

	# check if previously some criteria were selected, session is used to get them back
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


	# the actual algorithm starts here

	# data required to call the first API
	url = "https://movies-tvshows-data-imdb.p.rapidapi.com/"

	querystring = {"type": "get-random-movies", "page": "1"}

	headers = {
		'x-rapidapi-key': "4cb114e391msh37a075783e37650p16a360jsn2423cdf1eec9",
		'x-rapidapi-host': "movies-tvshows-data-imdb.p.rapidapi.com"
	}


	number_of_checked_genres_boxes = len(indices_of_checked_genres)
	number_of_checked_ranges_of_years_boxes = len(indices_of_checked_ranges_of_years)
	found = False

	# determine how many films should the algorithm check (if times = 1, then 20 are checked)
	counter, times = 0, 5

	# set default values if a required movie was not found
	imdb_rating = poster_url = movie_title = genres = year_of_movie = plot = actors = directors = runtime = trailer = language = awards = None

	# the code which queries the APIs and check if received movies satisfy the criteria
	while not found and counter < times:
		# check if the connection with the API was made
		try:
			response = requests.request("GET", url, headers=headers, params=querystring) #, timeout=5 )
			data = response.json()
			i = index = 0
		except:
			counter += 1
			continue

		# go through 20 random movies received from the API and check if they meet the criteria
		while i < 20 and not found:
			try:
				# a shortcut, otherwise I'd have needed to use this line every time I wanted to take data from the 'data'
				movie = data["movie_results"][i]

				genres = movie["genres"]

				# this is necessary to randomly pick one genre of all genres to not check one genre all the time the first
				copy_of_indices_of_checked_genres = indices_of_checked_genres.copy()
				
				id = movie["imdb_id"]
				year_of_movie = int(movie["year"])
				movie_title = movie["title"]

				# possible (rarely) to get movies with year = 0, such movies are skipped (inaccurate data)
				# once I encoutered a movie with any genres and got an error because of that
				if year_of_movie == 0 or len(genres) == 0:
					i += 1
					continue

				found_movie_within_year_range = False

				# check if the movie appears in the selected range(s) of years, if any were selected
				if 0 not in indices_of_checked_ranges_of_years and number_of_checked_ranges_of_years_boxes != 0:
					for x in range(number_of_checked_ranges_of_years_boxes):
						years = ranges_of_years[indices_of_checked_ranges_of_years[x]]
						
						# check if not the last range was selected
						if indices_of_checked_ranges_of_years[x] != number_of_different_ranges_of_years-1:
							if years[0] <= year_of_movie <= years[1]:
								found_movie_within_year_range = True
								break
						else:
							if years > year_of_movie:
								found_movie_within_year_range = True
								break

					# take a new movie if it is not in the right range
					if not found_movie_within_year_range:
						i += 1
						continue


				found_corresponding_genre = False

				# check if the movie has any of the selected genre
				if "checked" in checked_genres:
					for j in range(number_of_checked_genres_boxes):
						random.shuffle(copy_of_indices_of_checked_genres)
						if names_of_genres[copy_of_indices_of_checked_genres[-1]] in genres:
							index = i
							found_corresponding_genre = True
							break
						else:
							copy_of_indices_of_checked_genres.remove(copy_of_indices_of_checked_genres[-1])
            
					if not found_corresponding_genre:
						i += 1
						continue


				trailer = movie["youtube_trailer_key"].strip()
				if trailer:
					trailer = "https://www.youtube.com/embed/" + trailer

				# if genres and years met the criteria, then the rating is checked using the OMDB API
				respString = 'http://www.omdbapi.com/?i=' + id + '&apikey=b3814b2' 
				r = requests.get(respString) #, timeout=1)
				dictionary = r.json()

				poster_url = dictionary["Poster"].strip()
				imdb_rating = dictionary["imdbRating"]
				plot = dictionary["Plot"]
				actors = dictionary["Actors"]
				directors = dictionary["Director"]
				runtime = dictionary["Runtime"]
				language = dictionary["Language"]
				awards = dictionary["Awards"].strip()

				if awards == "N/A":
					awards = ""

				# it is possible to get "N/A" so it cannot be converted to a float at first
				# check if the connection was made with the API
				# check if the poster is provided 
				if imdb_rating == "N/A" and chosen_rating != 0 or dictionary["Response"] != "True" or poster_url == "" or poster_url=="N/A":
					i += 1
					continue

				if imdb_rating == "N/A":
					found = True
					break
				else:
					imdb_rating = float(imdb_rating)

				# if the rating meets the given criteria, so it means the movie was found, as it is checked the last
				if imdb_rating >= chosen_rating:
					found = True
					break

				i += 1

			except:
				i += 1

		counter += 1
    

	if not found:
		error_message = "Please try again!"
	else:
		error_message = ""


	return render_template(
		'suggestMeMovies.html',
		title='Suggest Me Movies',
		names_of_genres=names_of_genres,
		checked_genres=checked_genres,
		number_of_different_genres=number_of_different_genres,
		ratings=ratings,
		ratings_texts=ratings_texts,
		chosen_rating=chosen_rating,
		number_of_different_ratings=number_of_different_ratings,
		number_of_different_ranges_of_years=number_of_different_ranges_of_years,
		ranges_of_years_text=ranges_of_years_text,
		checked_ranges_of_years=checked_ranges_of_years,
		error_message=error_message,
		movie_title=movie_title,
		genres=genres,
		rating=imdb_rating,
		year_of_movie=year_of_movie,
		poster=poster_url,
		plot=plot,
		actors=actors,
		directors=directors,
		runtime=runtime,
		trailer=trailer,
		language=language,
		awards=awards
	)
