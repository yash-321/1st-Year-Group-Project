from flask import Flask


def create_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = "some_random_characters_are_okay"

	return app