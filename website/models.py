from . import login_manager, db
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
	responses = db.relationship('Response')
	blacklisted = db.relationship('Blacklist')
	reviews = db.relationship('Review')

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
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	movie_id = db.Column(db.Integer, nullable=False)

class Review(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	movie_id = db.Column(db.Integer, nullable=False)
	data = db.Column(db.String(10000), nullable=False)
	date = db.Column(db.DateTime(timezone=True), default=datetime.now())
	rating = db.Column(db.Float, nullable=False)
	spoiler_tag = db.Column(db.Boolean)

