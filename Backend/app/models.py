import os
import base64
from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy

login_manager = LoginManager()

favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True))

user_recipes = db.Table('user_recipes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True))

latest_users = db.Table('latest_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('timestamp', db.DateTime, default=datetime.utcnow, nullable=False))

@login.user_loader
def get_a_user_by_id(user_id):
    return db.session.get(User, user_id)

# Define a function to generate the SQL ORDER BY clause based on the sort_by and order query parameters
def order_func(sort_by, order):
    """
    Generate the SQL ORDER BY clause based on the sort_by and order query parameters
    """
    if sort_by == 'title':
        return f"{sort_by} {order}"
    elif sort_by == 'date_created':
        return f"{sort_by} {order}"
    elif sort_by == 'favorite_count':
        return f"(SELECT COUNT(*) FROM favorites WHERE recipe.id = favorites.recipe_id) {order}"
    else:
        return 'date_created DESC'
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
    recipes = db.relationship('Recipe', secondary=user_recipes, backref=db.backref('users', lazy='dynamic'))
    api_recipe = db.Column(db.Boolean, default=False)  # 
   

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = generate_password_hash(kwargs.get('password'))
        
    def __repr__(self):
        return f"<User {self.id}|{self.username}>"
    
    def to_dict(self):
        return {
        "id": self.id,
        "first_name": self.first_name,
        "last_name": self.last_name,
        "email": self.email,
        "username": self.username,
        }

    def check_password(self, password_guess):
        return check_password_hash(self.password, password_guess)

def store_recipes(recipes, user_id):
    if not current_user.is_authenticated or not current_user.is_active:
        return

    for recipe in recipes:
        existing_recipe = Recipe.query.filter_by(id=recipe['id']).first()

        if not existing_recipe:
            new_recipe = Recipe(
                id=recipe.get('id', ''),
                title=recipe.get('title', ''),
                link=recipe.get('sourceUrl', ''),
                image=recipe.get('image', ''),
                date_created=datetime.now(),
                user_id=user_id,
                api_recipe=True
            )
            db.session.add(new_recipe)
    db.session.commit()
    



@login.user_loader
def get_a_user_by_id(user_id):
    return db.session.get(User, user_id)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    link = db.Column(db.String(500))
    image = db.Column(db.String(500))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Allow NULL values for user_id
    latest_users = db.relationship('User', secondary=latest_users, backref=db.backref('latest_added_recipes', lazy='dynamic'), lazy='dynamic')
    api_recipe = db.Column(db.Boolean, default=False)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # remove seconds from the datetime
        self.date_created = datetime.utcnow().replace(microsecond=0)  

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<Recipe {self.id}|{self.title}>"

    def to_dict(self, current_user=None):
        if current_user is not None:
            is_favorite = current_user in self.favorited_by.all()
        else:
            is_favorite = False
        # Include the username of each user who favorited the recipe
        favorited_by_usernames = [user.username for user in self.favorited_by.all()]
        
        formatted_date = self.date_created.strftime('%B %d, %Y %I:%M %p')

        return {
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "date_created": formatted_date,
            "author": User.query.get(self.user_id).to_dict(),
            "is_favorite": is_favorite,
            "image": self.image,
            "favorited_by_usernames": favorited_by_usernames,
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
        
    def favorite_count(self):
        return self.favorited_by.count()

