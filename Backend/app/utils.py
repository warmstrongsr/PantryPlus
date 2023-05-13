from app import app, db, forms, models
from flask import Flask, render_template, url_for, flash, redirect, request, abort, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc, text, func, literal, cast, String, or_
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.orm import aliased
from app.apikey import API_KEY
from app.forms import SignUpForm, LoginForm, AddRecipeForm, SearchForm
from app.models import User, Recipe, favorites, db, store_recipes,  store_database_recipes,  delete_null_title_recipes
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import math
import html
import requests, random
import json
from sqlalchemy import func


spoonacular_api_key = API_KEY

def get_favorite_and_random_recipes(user_id):
    # Query the user's favorite recipes
    favorite_recipes = (
        db.session.query(Recipe)
        .join(favorites)
        .filter(favorites.user_id == user_id)
        .order_by(favorites.date_favorited.desc())
        .all()
    )
    # Calculate the remaining number of recipes to get
    num_random_recipes = 25 - len(favorite_recipes)

    if num_random_recipes > 0:
        # Query random recipes, excluding the user's favorite recipes
        random_recipes = (
            db.session.query(Recipe)
            .filter(Recipe.title.isnot(None), Recipe.id.notin_([r.id for r in favorite_recipes]))
            .order_by(func.random())
            .limit(num_random_recipes)
            .all()
        )
        # Combine the favorite and random recipes
        recipes = favorite_recipes + random_recipes
    else:
        # If there are already 25 or more favorite recipes, just return them
        recipes = favorite_recipes

    return recipes


# Only use filtered recipes from the database
def get_filtered_recipes(recipes):
    return [recipe for recipe in recipes if recipe.has_required_info()]

# Example to follow
def get_top_favorited_recipes(limit=10):
    top_favorited_recipes = db.session.query(Recipe, db.func.count(favorites.c.user_id).label('total_favorites'))\
        .join(favorites)\
        .group_by(Recipe)\
        .order_by(db.desc('total_favorites'))\
        .limit(limit)\
        .all()
    
    return get_filtered_recipes(top_favorited_recipes)