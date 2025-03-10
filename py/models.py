from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')  # Default role is 'user'
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    institute_name = db.Column(db.String(255), nullable=True)

    # Relationship with bookmarks (One-to-many)
    bookmarks = db.relationship('Bookmark', backref='user', lazy=True)
    resources = db.relationship('Resource', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

# Resource Model
class Resource(db.Model):
    __tablename__ = 'resources'

    resource_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    author_name = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who submitted the resource
    link = db.Column(db.String(255), nullable=True)
    category = db.Column(db.Enum('tutorial', 'research', 'github', 'course', 'blog', 'documentation'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')

    # Relationship with User (many-to-one)
    user = db.relationship('User', backref='resources', lazy=True)

    def __repr__(self):
        return f'<Resource {self.title}>'

# Bookmark Model
class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.resource_id'), nullable=False)

    # Relationship with Resource (many-to-one)
    resource = db.relationship('Resource', backref='bookmarks', lazy=True)

    def __repr__(self):
        return f'<Bookmark User {self.user_id} Resource {self.resource_id}>'
