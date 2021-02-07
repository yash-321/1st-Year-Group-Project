import secrets
import os
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from website.account_forms import RegistrationForm
from website import app


@app.route("/")


@app.route("/base")
def home():
	return render_template('base.html', title='Home')

@app.route("/login_register")
def login_register():
	return render_template('login_register.html', title='Login')

@app.route("/index")
def index():
	return render_template('index.html', title='Index')

@app.route("/seeMovieReview")
def seeMovieReview():
	return render_template('seeMovieReview.html', title='Movie Reviews')

@app.route("/suggestMeMovies")
def suggestMeMovies():
	return render_template('suggestMeMovies.html', title='Suggest Me a Movie')

@app.route("/writeReviews")
def writeReviews():
	return render_template('writeReviews.html', title='Write Reviews')

@app.route("/detailed_review")
def detailed_review():
	return render_template('detailed_review.html', title='Detailed Reviews')

@app.route("/account")
def account():
	return render_template('account.html', title='Detailed Reviews')







