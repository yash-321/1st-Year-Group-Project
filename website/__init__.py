from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = "some_random_characters_are_okay"

from website import views