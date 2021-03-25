from website import login_manager, db
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	display_name = db.Column(db.String(20), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	question_1 = db.Column(db.String(20), nullable=False)
	question_2 = db.Column(db.String(20), nullable=False)
	question_3 = db.Column(db.String(20), nullable=False)
	responses = db.relationship('Response')
	blacklisted = db.relationship('Blacklist')
	reviews = db.relationship('Review')
	whitelisted = db.relationship('Whitelist')

	def __repr__(self):
		return f"User('{self.username}', '{self.display_name}')"

class Question(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	question = db.Column(db.String(200), nullable=False)

class Response(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False)
	question_id = db.Column(db.Integer,db.ForeignKey('question.id'), nullable=False)
	response = db.Column(db.String(20), nullable=False)

class Blacklist(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	movie_id = db.Column(db.String(20), nullable=False)
	poster = db.Column(db.String(200))

class Whitelist(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	movie_id = db.Column(db.String(20), nullable=False)
	poster = db.Column(db.String(200))

class Review(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	movie_id = db.Column(db.String(20), nullable=False)
	title = db.Column(db.String(50), nullable=False)
	data = db.Column(db.Text, nullable=False)
	date = db.Column(db.DateTime(timezone=True), default=datetime.now())
	rating = db.Column(db.String(70), nullable=False)
	spoiler_tag = db.Column(db.Boolean)

class Movies(db.Model):
	movie_id = db.Column(db.String(20), primary_key=True, unique=True)
	title = db.Column(db.String(50), nullable=False)
	rating = db.Column(db.String(20))
	poster = db.Column(db.String(200), nullable=False)
	genres = db.Column(db.String(100), nullable=False)
	year = db.Column(db.Integer, nullable=False)
	plot = db.Column(db.String(100000), nullable=False)
	actors = db.Column(db.String(100000), nullable=False)
	directors = db.Column(db.String(100000), nullable=False)
	runtime = db.Column(db.String(20), nullable=False)
	trailer = db.Column(db.String(200))
	language = db.Column(db.String(50))
	awards = db.Column(db.String(100), nullable=False)
