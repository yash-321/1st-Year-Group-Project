import secrets
from flask import Blueprint, render_template, request, session, url_for, flash, redirect
from flask_login import current_user
from website import app, db
from website.models import User, Blacklist, Whitelist, Movies
import random 
import requests
from datetime import datetime, timedelta

movies = Blueprint('movies', __name__)

# the period of time for how long data is saved on the website
app.secret_key = "df78sf845s65fsf9sd5f2fg13513sdfsa"
app.permanent_session_lifetime = timedelta(minutes=10)


@movies.route("/searchMovies/", methods=['GET', 'POST'])
@movies.route("/searchMovies/page=<page>", methods=['GET', 'POST'])
def seeMovieReview(page = 1):
	# initialise the required data
	search_result = ""
	number_of_movies = 0
	number_of_received_movies = 0
	titles = []
	years = []
	IDs = []
	types = []
	posters = []
	error_message = ""

	if request.method == 'POST':
		# session saves the typed keyword
		session.permanent = True

		search_result = request.form.get("search").strip()
		
		if search_result:
			session["search"] = search_result
		else:
			# if nothing was typed when do not query the API
			session.pop("search", None)


	emptySearchBox = False
		
	# if anything was typed in the search bar when query the API to get movies by keyword
	# otherwise, query the other API to receive 5 random popular movies
	if "search" in session:
		try:
			number_of_movies = 20

			pages = list()
			page = int(page)

			pages.append(page*2-1)
			pages.append(page*2)

			search_result = session["search"]

			api_key = ""
			for i in range(2):
				respString = 'http://www.omdbapi.com/?s=' + search_result + api_key + str(pages[i]) 
				r = requests.get(respString) 
				dictionary = r.json()
				if dictionary['Response'] == 'True':
					data = dictionary["Search"]
					for movie in data:
						titles.append(movie['Title'])
						years.append(movie['Year'])
						IDs.append(movie['imdbID'])
						posters.append(movie['Poster'])

					number_of_received_movies = len(IDs)
				else:
					if not IDs:
						error_message = "Try again! None movies were found..."

		except Exception as e:
			error_message = "Try again! None movies were found..."
	else:
		try:
			emptySearchBox = True
			number_of_movies = 20

			this_year = datetime.now().year

			search_result = ""

			# get this and last two years movies
			this_years_movies = Movies.query.filter_by(year=this_year).all()
			movies = Movies.query.filter_by(year=this_year-1).all()
			movies += this_years_movies + Movies.query.filter_by(year=this_year-2).all()
			number = len(movies)

			found_movies = False

			# to make sure the loop terminates
			counter = 0
			while not found_movies and counter < 100:
				try:
					num = random.randint(1, number)
					movie = movies[num]

					if movie.movie_id not in IDs and movie.poster != 'N/A':
						titles.append(movie.title)
						years.append(movie.year)
						IDs.append(movie.movie_id)
						posters.append(movie.poster)

					if len(titles) == number_of_movies:
						found_movies = True
				
				except Exception as e:
					pass

				counter += 1

		except Exception as e:
			error_message = "Try again! None movies were found..."


	# validate if page data type is not a string
	try:
		page = int(page)
	except Exception as e:
		error_message = "Try again! Invalid page number was provided!"

	return render_template(
		'seeMovieReview.html',
	 	title='Search Movies',
	 	search_result=search_result,
	 	number_of_movies=number_of_movies,
		number_of_received_movies=number_of_received_movies,
	 	titles=titles,
	 	years=years,
	 	IDs=IDs,
	 	posters=posters,
	 	error_message=error_message,
	 	page=page,
	 	emptySearchBox=emptySearchBox)


def check_genres(checked_genres, number_of_checked_genres_boxes, copy_of_indices_of_checked_genres, names_of_genres, genres):
	if "checked" in checked_genres:
		for j in range(number_of_checked_genres_boxes):
			random.shuffle(copy_of_indices_of_checked_genres)
			if names_of_genres[copy_of_indices_of_checked_genres[-1]] in genres:
				return True
			else:
				copy_of_indices_of_checked_genres.remove(copy_of_indices_of_checked_genres[-1])

		return False
	else:
		return True


def check_movie_year(indices_of_checked_ranges_of_years, number_of_checked_ranges_of_years_boxes, 
					number_of_different_ranges_of_years, ranges_of_years, year_of_movie):
	# check if the movie appears in the selected range(s) of years, if any were selected
	if 0 not in indices_of_checked_ranges_of_years and number_of_checked_ranges_of_years_boxes != 0:
		for x in range(number_of_checked_ranges_of_years_boxes):
			years = ranges_of_years[indices_of_checked_ranges_of_years[x]]
			
			# check if not the last range was selected
			if indices_of_checked_ranges_of_years[x] != number_of_different_ranges_of_years-1:
				if years[0] <= year_of_movie <= years[1]:
					return True
			else:
				if years > year_of_movie:
					return True
		return False
	else:
		return True


def check_movie_language(languages_texts, number_of_checked_language_boxes, 
					number_of_different_languages, indices_of_checked_languages, movie_language):
	# check if the movie is in the selected language(s), if any were selected
	if 0 not in indices_of_checked_languages and number_of_checked_language_boxes != 0:
		for x in range(number_of_checked_language_boxes):
			language = languages_texts[indices_of_checked_languages[x]]
			if language in movie_language:
				return True

		return False
	else:
		return True


def check_db_for_movie(movie, blacklisted_movies_ids, indices_of_checked_genres,
						languages_texts, number_of_checked_language_boxes, number_of_different_languages, 
						indices_of_checked_languages, checked_genres, number_of_checked_genres_boxes, names_of_genres,
						indices_of_checked_ranges_of_years, number_of_checked_ranges_of_years_boxes, 
						number_of_different_ranges_of_years, ranges_of_years, chosen_rating):

	# check if that movie is not in the blacklist
	# if it is, then skip this movie
	if blacklisted_movies_ids:
		if movie.movie_id in blacklisted_movies_ids:
			return False

	copy_of_indices_of_checked_genres = indices_of_checked_genres.copy()

	if movie.year == 0 or movie.genres == "" or type(movie.year) == str:
		return False

	found_language = check_movie_language(languages_texts, number_of_checked_language_boxes, 
					number_of_different_languages, indices_of_checked_languages, movie.language)

	if not found_language:
		return False

	found_corresponding_genre = check_genres(checked_genres, number_of_checked_genres_boxes, copy_of_indices_of_checked_genres, names_of_genres, movie.genres)
	
	if not found_corresponding_genre:
		return False

	found_movie_within_year_range = check_movie_year(
										indices_of_checked_ranges_of_years, 
										number_of_checked_ranges_of_years_boxes, 
										number_of_different_ranges_of_years,
										ranges_of_years, 
										movie.year)
		
	if not found_movie_within_year_range:
		return False

	if movie.rating == "N/A" and chosen_rating != 0 or movie.poster == "" or movie.poster == "N/A":
		return False

	return True


@movies.route("/suggestMeMovies", methods=['GET', 'POST'])
def suggestMeMovies():
	# the tuples and lists to save the required data for criteria

	names_of_genres = ("Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", 
						"Documentary", "Drama", "Family", "Fantasy", "History", "Horror", 
						 "Mystery", "Romance", "Sci-Fi", "Thriller")

	indices_of_checked_genres = []
	number_of_different_genres = len(names_of_genres)
	checked_genres = [""]*number_of_different_genres


	ratings = (0, 7, 6.5, 6, 5.5, 5, 4.5)
	ratings_texts = ("Any Ratings", "Rated over 7",
					"Rated over 6.5","Rated over 6","Rated over 5.5",
					"Rated over 5", "Rated over 4.5")
	chosen_rating = 0
	number_of_different_ratings = len(ratings)


	languages_identifiers = (0, 1, 2, 3, 4)
	languages_texts = ("Any Language", "English",
					"French","Japanese","Spanish")
					
	number_of_different_languages = len(languages_identifiers)
	indices_of_checked_languages = []
	checked_languages = [""]*number_of_different_languages


	ranges_of_years_text = ("All years", "2010 – now", "2000 – 2009", "1990 – 1999",
							"1980 – 1989", "1960 – 1979", "Older than 1960")

	ranges_of_years = (0, (2010, 2021), (2000, 2009), (1990, 1999),
					  (1980, 1989), (1960, 1979), 1960)

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
		
		for i in range(number_of_different_languages):
			if request.form.get(languages_texts[i]):
				indices_of_checked_languages.append(i)
				checked_languages[i] = "checked"
				session["checked_languages" + str(i)] = "checked"
			else:
				if ("checked_languages" + str(i)) in session:
					session.pop("checked_languages" + str(i), None)


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
			

	for i in range(number_of_different_languages):
		if ("checked_languages" + str(i)) in session and checked_languages[i] != "checked":
			checked_languages[i] = "checked"
			indices_of_checked_languages.append(i)


	# ----------------- the actual algorithm starts here -----------------

	# data required to call the first API
	url = "https://movies-tvshows-data-imdb.p.rapidapi.com/"

	querystring = {"type":"get-random-movies","page":"1"}

	headers = {
		'x-rapidapi-key': "",
		'x-rapidapi-host': "movies-tvshows-data-imdb.p.rapidapi.com"
	}

	movies = Movies.query.all()

	number_of_checked_genres_boxes = len(indices_of_checked_genres)
	number_of_checked_ranges_of_years_boxes = len(indices_of_checked_ranges_of_years)
	number_of_checked_language_boxes = len(indices_of_checked_languages)
	found = False

	# determine how many films should the algorithm check (if times = 1, then 20 are checked)
	counter, times = 0, 3

	# set default values if a required movie was not found
	imdb_rating = poster_url = movie_title = genres = year_of_movie = plot = actors = directors = runtime = trailer = language = awards = id = None

	all_movies_in_db = Movies.query.all()
	length = len(all_movies_in_db)

	# get the blacklisted movies if a user is logged in
	blacklisted_movies_ids = list()

	if current_user.is_authenticated:
		user = User.query.filter_by(username=current_user.username).first()
		blacklisted_movies = Blacklist.query.filter_by(user_id=user.id).all()

		for movie in blacklisted_movies:
			blacklisted_movies_ids.append(movie.movie_id)

	# to make the algorithm a bit faster I firstly check some movies from the database 
	# so I could much faster provide a movie let's say when any criteria were selected
	check_this_number_of_all_movies_in_db = 20
	random_offset = random.randint(1, length-check_this_number_of_all_movies_in_db)
	movies = Movies.query.limit(check_this_number_of_all_movies_in_db).offset(random_offset).all()
	random.shuffle(movies)

	for movie in movies:
		try:
			valid_movie = check_db_for_movie(movie, blacklisted_movies_ids, indices_of_checked_genres,
						languages_texts, number_of_checked_language_boxes, number_of_different_languages, 
						indices_of_checked_languages, checked_genres, number_of_checked_genres_boxes, names_of_genres,
						indices_of_checked_ranges_of_years, number_of_checked_ranges_of_years_boxes, 
						number_of_different_ranges_of_years, ranges_of_years, chosen_rating)

			if not valid_movie:
				continue
			
			if movie.rating == "N/A":
				found = True
			else:
				movie.rating = float(movie.rating)

			# if the rating meets the given criteria, so it means the movie was found, as it is checked the last
			if not found:
				if movie.rating >= chosen_rating:
					found = True

			if found:
				id = movie.movie_id
				movie_title = movie.title
				genres = movie.genres.split(", ")
				imdb_rating = movie.rating
				year_of_movie = movie.year
				poster_url = movie.poster
				plot = movie.plot
				actors = movie.actors
				directors = movie.directors
				runtime = movie.runtime
				trailer = movie.trailer
				language = movie.language
				awards = movie.awards
				break
		except Exception as e:
			pass


	# the code which queries the APIs and check if received movies satisfy the criteria
	while not found and counter < times:
		# check if the connection with the API was made
		try:
			response = requests.request("GET", url, headers=headers, params=querystring) #, timeout=5 )
			data = response.json() 
		except Exception as e:
			counter += 1
			continue

		i = 0
		# go through 20 random movies received from the API and check if they meet the criteria
		while i < 20 and not found:
			try:
				# a shortcut, otherwise I'd have needed to use this line every time I wanted to take data from the 'data'
				movie = data["movie_results"][i]
				genres = movie["genres"]
				# this is necessary to randomly pick one genre of all genres to not check one genre all the time the first
				copy_of_indices_of_checked_genres = indices_of_checked_genres.copy()
				
				id = movie["imdb_id"]
				# check if that movie is not in the blacklist
				# if it is, then skip this movie
				if blacklisted_movies_ids:
					if id in blacklisted_movies_ids:
						i += 1
						continue

				year_of_movie = int(movie["year"])
				movie_title = movie["title"]

				# possible (rarely) to get movies with year = 0, such movies are skipped (inaccurate data)
				# once I encoutered a movie with any genres and got an error because of that
				if year_of_movie == 0 or len(genres) == 0 or genres == None:
					i += 1
					continue

				found_movie_within_year_range = check_movie_year(
												indices_of_checked_ranges_of_years, 
												number_of_checked_ranges_of_years_boxes,
												number_of_different_ranges_of_years, 
												ranges_of_years, 
												year_of_movie)
				
				if not found_movie_within_year_range:
					i += 1
					continue

				found_corresponding_genre = check_genres(checked_genres, number_of_checked_genres_boxes, copy_of_indices_of_checked_genres, names_of_genres, genres)
				
				if not found_corresponding_genre:
					i += 1
					continue

				trailer = movie["youtube_trailer_key"].strip()
				
				if trailer:
					trailer = "https://www.youtube.com/embed/" + trailer

				# if genres and years met the criteria, then the rating is checked using the OMDB API
				api_key = ""
				respString = 'http://www.omdbapi.com/?i=' + id + api_key
				r = requests.get(respString) #, timeout=1)
				dictionary = r.json()

				language = dictionary["Language"]
				poster_url = dictionary["Poster"].strip()
				imdb_rating = dictionary["imdbRating"]
				plot = dictionary["Plot"]
				actors = dictionary["Actors"]
				directors = dictionary["Director"]
				runtime = dictionary["Runtime"]
				awards = dictionary["Awards"].strip()

				check_not_in_db = Movies.query.filter_by(movie_id=id).first()

				if not check_not_in_db:
					movie = Movies(movie_id=id, title=movie_title, rating=imdb_rating, poster=poster_url, genres=", ".join(genres),
									year=year_of_movie, plot=plot, actors=actors, directors=directors, runtime=runtime,
									language=language, awards=awards, trailer=trailer)
					
					db.session.add(movie)
					db.session.commit()
				else:
					movie = check_not_in_db

					# add the trailer to the db if it was not added before
					if not movie.trailer and trailer:
						movie.trailer = trailer
						db.session.commit()

				found_language = check_movie_language(languages_texts, number_of_checked_language_boxes, 
													number_of_different_languages, indices_of_checked_languages, language)

				if not found_language:
					i += 1
					continue

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

			except Exception as e:
				i += 1

		check_this_number_of_all_movies_in_db = 20
		random_offset = random.randint(1, length-check_this_number_of_all_movies_in_db)
		movies = Movies.query.limit(check_this_number_of_all_movies_in_db).offset(random_offset).all()
		random.shuffle(movies)
		
		for movie in movies:
			try:
				valid_movie = check_db_for_movie(movie, blacklisted_movies_ids, indices_of_checked_genres,
						languages_texts, number_of_checked_language_boxes, number_of_different_languages, 
						indices_of_checked_languages, checked_genres, number_of_checked_genres_boxes, names_of_genres,
						indices_of_checked_ranges_of_years, number_of_checked_ranges_of_years_boxes, 
						number_of_different_ranges_of_years, ranges_of_years, chosen_rating)

				if not valid_movie:
					continue
				
				if movie.rating == "N/A":
					found = True
				else:
					movie.rating = float(movie.rating)

				# if the rating meets the given criteria, so it means the movie was found, as it is checked the last
				if not found:
					if movie.rating >= chosen_rating:
						found = True

				if found:
					id = movie.movie_id
					movie_title = movie.title
					genres = movie.genres.split(", ")
					imdb_rating = movie.rating
					year_of_movie = movie.year
					poster_url = movie.poster
					plot = movie.plot
					actors = movie.actors
					directors = movie.directors
					runtime = movie.runtime
					trailer = movie.trailer
					language = movie.language
					awards = movie.awards
					break
			except Exception as e:
				pass

		counter += 1
    
	movies = Movies.query.all()

	if not found:
		try:
			# shuffle the list to avoid getting the same movie as the first all the time
			random.shuffle(all_movies_in_db)

			for movie in all_movies_in_db:
				# check if that movie is not in the blacklist
				# if it is, then skip this movie
				valid_movie = check_db_for_movie(movie, blacklisted_movies_ids, indices_of_checked_genres,
						languages_texts, number_of_checked_language_boxes, number_of_different_languages, 
						indices_of_checked_languages, checked_genres, number_of_checked_genres_boxes, names_of_genres,
						indices_of_checked_ranges_of_years, number_of_checked_ranges_of_years_boxes, 
						number_of_different_ranges_of_years, ranges_of_years, chosen_rating)

				if not valid_movie:
					continue

				if movie.rating == "N/A":
					found = True
				else:
					movie.rating = float(movie.rating)

				# if the rating meets the given criteria, so it means the movie was found, as it is checked the last
				if not found:
					if movie.rating >= chosen_rating:
						found = True

				if found:
					id = movie.movie_id
					movie_title = movie.title
					genres = movie.genres.split(", ")
					imdb_rating = movie.rating
					year_of_movie = movie.year
					poster_url = movie.poster
					plot = movie.plot
					actors = movie.actors
					directors = movie.directors
					runtime = movie.runtime
					trailer = movie.trailer
					language = movie.language
					awards = movie.awards
					break

		except Exception as e:
			pass

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
		languages_identifiers=languages_identifiers,
		languages_texts=languages_texts,
		indices_of_checked_languages=indices_of_checked_languages,
		checked_languages=checked_languages,
		number_of_different_languages=number_of_different_languages,
		number_of_different_ranges_of_years=number_of_different_ranges_of_years,
		ranges_of_years_text=ranges_of_years_text,
		checked_ranges_of_years=checked_ranges_of_years,
		error_message=error_message,
		movie_id=id,
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


# Saving movie to white or blacklist
@movies.route('/save_movie', methods=['POST'])
def save_movie():
	data = request.form.to_dict()

	if not current_user.is_authenticated:
		if data['buttonpressed'] == "whitelistbtn":
			flash(f'Please login to add a movie to your whitelist', 'danger')
		elif data['buttonpressed'] == "blacklistbtn":
			flash(f'Please login to add a movie to your blacklist', 'danger')
		session['movieID'] = data['currentMovieID']
		return url_for('usersReviews.login')
	else:
		user = User.query.filter_by(username=current_user.username).first()
		if data['buttonpressed'] == "whitelistbtn":
			check = Whitelist.query.filter_by(user_id=user.id).all()
			# checks if movie is alredy in users whitelist
			for movies in check:
				if movies.movie_id == data['currentMovieID']:
					db.session.delete(movies)
					db.session.commit()
					return "RemovedW"
			check = Blacklist.query.filter_by(user_id=user.id).all()
			for movies in check:
				# checks if movie is in users blacklist
				if movies.movie_id == data['currentMovieID']:
					white = Whitelist(title=data['currentMovieTitle'], user_id=user.id, movie_id=data['currentMovieID'], poster=data['currentMoviePoster'])
					db.session.add(white)
					db.session.delete(movies)
					db.session.commit()
					return "BtoW"
			white = Whitelist(title=data['currentMovieTitle'], user_id=user.id, movie_id=data['currentMovieID'], poster=data['currentMoviePoster'])
			db.session.add(white)
			db.session.commit()
			return "SavedW"
			
		elif data['buttonpressed'] == "blacklistbtn":
			check = Blacklist.query.filter_by(user_id=user.id).all()
			for movies in check:
				# checks if movie is alredy in users blacklist
				if movies.movie_id == data['currentMovieID']:
					db.session.delete(movies)
					db.session.commit()
					return "RemovedB"
			check = Whitelist.query.filter_by(user_id=user.id).all()
			for movies in check:
				# checks if movie is in users blacklist
				if movies.movie_id == data['currentMovieID']:
					black = Blacklist(title=data['currentMovieTitle'], user_id=user.id, movie_id=data['currentMovieID'], poster=data['currentMoviePoster'])
					db.session.add(black)
					db.session.delete(movies)
					db.session.commit()
					return "WtoB"
			black = Blacklist(title=data['currentMovieTitle'], user_id=user.id, movie_id=data['currentMovieID'], poster=data['currentMoviePoster'])
			db.session.add(black)
			db.session.commit()
			return "SavedB"
			
		return "Something went wrong"