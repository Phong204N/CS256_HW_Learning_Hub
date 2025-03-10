from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    # Columns definition
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    institute_name = db.Column(db.String(255), nullable=True)

    # Updated relationship with unique backref
    resources = db.relationship('Resource', backref='user_resource', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Resource(db.Model):
    __tablename__ = 'resources'

    resource_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    author_name = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to users table
    status = db.Column(db.String(50), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Use datetime.utcnow() here

    def __repr__(self):
        return f'<Resource {self.title}>'

# Bookmark Model
class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.resource_id'), nullable=False)

    resource = db.relationship('Resource', backref='bookmarks', lazy=True)

    def __repr__(self):
        return f'<Bookmark User {self.user_id} Resource {self.resource_id}>'
