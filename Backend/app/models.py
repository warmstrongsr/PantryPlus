import os
import base64
from datetime import datetime, timedelta
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
from app import db, login

login_manager = LoginManager()

favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True))

 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(75), nullable=False, unique=True)
    username = db.Column(db.String(75), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    favorites = db.relationship('Recipe', secondary=favorites, lazy='dynamic',
        backref=db.backref('favorited_by', lazy='dynamic'))
   

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = generate_password_hash(kwargs.get('password'))
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<User {self.id}|{self.username}>"

    def check_password(self, password_guess):
        return check_password_hash(self.password, password_guess)

@login.user_loader
def get_a_user_by_id(user_id):
    return db.session.get(User, user_id)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(200))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<Recipe {self.id}|{self.title}>"

    def to_dict(self):
        currrent_user = User.query.get(current_user_id)
        is_favorite = currrent_user in self.favorited_by.all()
        return {
            'id': self.id,
            'title': self.title,
            'link': self.link,
            'date_created': self.date_created,
            'author': User.query.get(self.user_id).to_dict(), 
            'is_favorite': True if self.user_id in self.favorites else False
        }

    def update(self, data):
        for field in data:
            if field not in {'title', 'content', 'user_id'}:
                continue
            setattr(self, field, data[field])
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        


