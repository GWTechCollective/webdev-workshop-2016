from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

DankPostCategory = db.Table('DankPostCategory',
                       db.Column('id', db.Integer, primary_key=True),
                       db.Column('dankpostId', db.Integer, db.ForeignKey('DankPost.id')),
                       db.Column('categoryId', db.Integer, db.ForeignKey('Category.id')))

class DankPost(db.Model):
    __tablename__ = 'DankPost'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=False)
    filename = db.Column(db.String(128), unique=False)
    dank_rank = db.Column(db.Integer, unique=False)
    timestamp = db.Column(db.DateTime, unique=False)
    categories = db.relationship('Category', secondary=DankPostCategory, backref='DankPost')

    def __init__(self, title, filename):
        self.title = title
        self.filename = filename
        self.dank_rank = 0
        self.timestamp = datetime.utcnow()

class Category(db.Model):
    __tablename__ = 'Category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False)
    dankposts = db.relationship('DankPost', secondary=DankPostCategory, backref='Category')

    def __init__(self, name):
        self.name = name

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    passhash = db.Column(db.String(128), unique=False)

    def __init__(self, username, passhash):
        self.username = username
        self.passhash = generate_password_hash(passhash)
