from flask import Blueprint, render_template

misc = Blueprint('misc', __name__)


@misc.route("/")
@misc.route("/home")
def home():
	return render_template('index.html', title='Home')
	#this should render index.html but since the inheritence isn't set up on it, using base.html instead.
	#return render_template('index.html', title='Home')


@misc.route("/privacyPolicy")
def privacyPolicy():
	return render_template('policy.html', title="Privacy Policy")


@misc.route("/termsOfUse")
def termOfUse():
	return render_template('termOfUse.html', title="Terms Of Use")
