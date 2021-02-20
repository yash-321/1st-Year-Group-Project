from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = "some_random_characters_are_okay"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'usersReviews.login'
login_manager.login_message_category = 'info'

from website.usersReviews.views import usersReviews
from website.movies.views import movies
from website.misc.views import misc

app.register_blueprint(usersReviews)
app.register_blueprint(movies)
app.register_blueprint(misc)
