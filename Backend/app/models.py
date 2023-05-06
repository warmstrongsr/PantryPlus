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

#****DELETE****DELETE***DELETE*****
def delete_null_title_recipes():
    null_title_recipes = Recipe.query.filter(Recipe.title.is_(None)).all()
    for recipe in null_title_recipes:
        db.session.delete(recipe)
    db.session.commit()


@login.user_loader
def get_a_user_by_id(user_id):
    return db.session.get(User, user_id)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    link = db.Column(db.String(500))
    image = db.Column(db.String(500))
    instructions = db.Column(db.Text)  # Add instructions column
    ingredients = db.Column(db.Text)  # Add instructions column
    summary = db.Column(db.Text) # Add summary column
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
            "author": User.query.get(self.user_id).to_dict(),
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
    
    @classmethod
    def get_recipes_by_user(cls, user_id, sort_by='title', order='asc', page=1, per_page=10):
        query = cls.query.filter(cls.user_id == user_id)
        if sort_by == 'favorites':
            query = query.outerjoin(favorites).group_by(cls.id).order_by(
                db.func.count(favorites.c.user_id).desc())
        else:
            query = query.order_by(getattr(cls, sort_by).asc() if order == 'asc' else getattr(cls, sort_by).desc())

        recipes = query.paginate(page=page, per_page=per_page, error_out=False).items
        valid_recipes = [recipe for recipe in recipes if recipe.get('title') and recipe.get('link')]
        total_pages = int(math.ceil(len(valid_recipes) / per_page))

        return {'recipes': valid_recipes, 'total_pages': total_pages}

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
            id=recipe.get('id', ''),
            title=recipe.get('title', ''),
            link=recipe.get('sourceUrl', ''),
            
            if not id or not title or not link:
                continue
                                # json.dump for storing
            new_recipe = Recipe(
                ingredients=json.dumps(recipe.get('ingredients', [])),
                image=recipe.get('image', ''),
                date_created=datetime.now(),
                instructions=recipe.get('instructions', ''),
                summary=recipe.get('summary', ''),
                user_id=user_id,
            )
            db.session.add(new_recipe)
            db.session.commit()

class RecipeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Recipe):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)

