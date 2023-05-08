import os
import base64
from datetime import datetime
from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from flask import current_app, Flask
from .models import db
import math
import json


favorites = db.Table('favorites',
                     db.Column('user_id', db.Integer,
                               db.ForeignKey('user.id')),
                     db.Column('recipe_id', db.Integer,
                               db.ForeignKey('recipe.id')),
                     db.Column('date_favorited', db.DateTime,
                               default=datetime.utcnow)
                     )

user_recipes = db.Table('user_recipes',
                        db.Column('user_id', db.Integer, db.ForeignKey(
                            'user.id'), primary_key=True),
                        db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True))

@login.user_loader
def get_a_user_by_id(user_id):
    return db.session.get(User, user_id)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(500))
    image = db.Column(db.String(500))
    instructions = db.Column(db.Text, nullable=True)
    ingredients = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True) # Add summary column
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=True)  # Allow NULL values for user_id
    favorited_by = db.relationship('User', secondary=favorites,
                                   backref=db.backref(
                                       'favorite_recipes', lazy=True, overlaps="favorited_users,favorites"),
                                   order_by=favorites.c.date_favorited.desc())
    users = db.relationship('User', secondary=user_recipes,
                            backref=db.backref('recipe_users', lazy='dynamic'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # remove seconds from the datetime
        self.date_created = datetime.utcnow().replace(microsecond=0)

        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<Recipe {self.id}|{self.title}>"
    
    def has_required_info(self):
        return (
            self.title
            and self.instructions
            and self.ingredients
            and self.summary
        )

    def to_dict(self, current_user=None):
        if current_user is not None:
            is_favorite = current_user in self.favorited_by.all()
        else:
            is_favorite = False
        # Include the username of each user who favorited the recipe
        favorited_by = [
            user.username for user in self.favorited_by]

        formatted_date = self.date_created.strftime('%B %d, %Y %I:%M %p')

        # json.loads for retrieving the recipe
        ingredients = json.loads(self.ingredients) if self.ingredients else []

        return {
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "date_created": formatted_date,
            "is_favorite": is_favorite,
            "image": self.image,
            "favorited_by": self.favorited_by,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "summary": self.summary,
            "users": self.users
        }

    def update(self, data):
        for field in data:
            if field not in {'title', 'content', 'user_id', 'instructions', 'ingredients', 'summary'}:
                continue
            setattr(self, field, data[field])
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def favorite_count(self):
        return self.favorited_by.count()
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(75), nullable=False, unique=True)
    username = db.Column(db.String(75), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    favorites = db.relationship('Recipe', secondary=favorites, backref=db.backref(
        'favorited_users', lazy=True, overlaps="favorited_by"), lazy='select')

    recipes = db.relationship(
        'Recipe', secondary=user_recipes, backref=db.backref('recipe_users', lazy='dynamic'))
    latest_added_recipes = db.relationship('Recipe', order_by=Recipe.date_created.desc())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = generate_password_hash(kwargs.get('password'))

    def __repr__(self):
        return f"<User {self.id}|{self.username}>"

    def to_dict(self):
        formatted_date = self.date_created.strftime("%Y-%m-%d %H:%M:%S")
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "username": self.username,
            "date_created": formatted_date,
        }

    def check_password(self, password_guess):
        return check_password_hash(self.password, password_guess)
    
def store_recipes(recipes, user_id):
    if not current_user.is_authenticated or not current_user.is_active:
        return

    for recipe in recipes:
        existing_recipe = Recipe.query.filter_by(id=recipe['id']).first()

        if not existing_recipe:
            # Create a new recipe if it doesn't exist
            new_recipe = Recipe(
                id=recipe.get('id', ''),
                title=recipe.get('title', ''),
                link=recipe.get('sourceUrl', ''),
                ingredients=json.dumps(recipe.get('extendedIngredients', [])),
                image=recipe.get('image', ''),
                date_created=datetime.now(),
                instructions=recipe.get('instructions', ''),
                summary=recipe.get('summary', ''),
                user_id=user_id,        
            )
            db.session.add(new_recipe)
            db.session.commit()
            print(new_recipe)
        else:
            # Update the existing recipe with new data
            existing_recipe.title = recipe.get('title', existing_recipe.title)
            existing_recipe.link = recipe.get('sourceUrl', existing_recipe.link)
            existing_recipe.ingredients = json.dumps(recipe.get('extendedIngredients', []))
            existing_recipe.image = recipe.get('image', existing_recipe.image)
            existing_recipe.instructions = recipe.get('instructions', existing_recipe.instructions)
            existing_recipe.summary = recipe.get('summary', existing_recipe.summary)

            db.session.commit()
            
def store_database_recipes(recipes, user_id):
    if not current_user.is_authenticated or not current_user.is_active:
        return

    for recipe in recipes:
        existing_recipe = Recipe.query.filter_by(id=recipe.id).first()

        if  existing_recipe:
            # Update the existing recipe with new data
            existing_recipe.title = recipe.title
            existing_recipe.link = recipe.link
            existing_recipe.ingredients = recipe.ingredients
            existing_recipe.image = recipe.image
            existing_recipe.instructions = recipe.instructions
            existing_recipe.summary = recipe.summary

            db.session.commit()

def get_top_favorited_recipes(limit=10):
    top_favorited_recipes = db.session.query(Recipe, db.func.count(favorites.c.user_id).label('total_favorites'))\
        .join(favorites)\
        .group_by(Recipe)\
        .order_by(db.desc('total_favorites'))\
        .limit(limit)\
        .all()
    
    return top_favorited_recipes

class RecipeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Recipe):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)

#****DELETE****DELETE***DELETE*****
def delete_null_title_recipes():
    null_title_recipes = Recipe.query.filter(Recipe.title.is_(None)).all()
    for recipe in null_title_recipes:
        db.session.delete(recipe)
    db.session.commit()