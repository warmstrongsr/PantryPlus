from flask import request, jsonify,Flask, render_template, url_for, flash, redirect, requests, abort, session
from app.models import Recipe, update_recipe, User, favorites, db, store_recipes, delete_null_title_recipes, User
from app import app, db, forms, models
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc, text, func, literal
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app.apikey import API_KEY
from app.forms import SignUpForm, LoginForm, AddRecipeForm, SearchForm
from app.routes import routes
import math
import requests, random
import json

# spoonacular_api_key = API_KEY


# def get_random_recipes():
#     num_recipes = 25 # number of random recipes to retrieve
#     random_recipes = Recipe.query.order_by(func.random()).limit(num_recipes).all()
#     return random_recipes


# def get_random_recipes():
#     api_key = spoonacular_api_key
#     url = f"https://api.spoonacular.com/recipes/random?number=100&apiKey={api_key}"
#     response = requests.get(url)
#     data = json.loads(response.text)
#     random_recipes = data['recipes']
#     return random_recipes

# def get_recipe_summary(recipe_id):
#     api_key = spoonacular_api_key
#     url = f"https://api.spoonacular.com/recipes/{recipe_id}/summary?apiKey={api_key}"
#     response = requests.get(url)
#     data = json.loads(response.text)
#     recipe_summary = data['summary']
#     return recipe_summary

# def update_missing_summaries():
#     # Get all recipes with a missing summary
#     recipes_to_update = Recipe.query.filter(Recipe.summary.is_(None)).all()

#     # Update each recipe
#     for recipe in recipes_to_update:
#         # Get the recipe data from the Spoonacular API
#         recipe_data = get_recipe_data(recipe.id)
        
#         if not recipe_data:
#             continue

#         # Update the recipe with the new summary
#         recipe.update({"summary": recipe_data.get("summary")})
        
        
# def get_recipe_data(recipe_id):
#     api_key = '<your_spoonacular_api_key>'
#     url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}'
#     response = requests.get(url)
#     if response.status_code == 200:
#         recipe_data = response.json()
#         return recipe_data
#     else:
#         return None


# @app.route('/index', methods=['GET', 'POST'])
# @login_required
# def index():
#     page = request.args.get('page', 1, type=int)
    
#     # Check the request method and handle the logic accordingly
#     if request.method == 'POST':
#         recipes = session.get('random_recipes', [])
#     else:
#         recipes = get_random_recipes()
#         user_id = int(current_user.get_id())  # Get the current user's ID
#         # store_recipes(recipes, user_id)  # Pass the user_id to the store_recipes function
#         session['random_recipes'] = recipes
        
#         recipe_dicts = []
#         for recipe in recipes:
#             recipe_id = recipe.id
#             recipe_title = recipe.title
#             recipe_image = recipe.image
#             recipe_link = f"https://spoonacular.com/recipes/{'-'.join(recipe_title.split(' '))}-{recipe_id}"
#             recipe_dict = {'id': recipe_id, 'title': recipe_title, 'image': recipe_image, 'link': recipe_link}
#             recipe_dicts.append(recipe_dict)

#         # Store the fetched recipes in the database
#         # if current_user.is_authenticated and current_user.is_active:
#         #     store_recipes(recipes, current_user.id)

#     # Filter out recipes with missing data
#     valid_recipes = [recipe for recipe in recipes if recipe.get('title') and recipe.get('sourceUrl')]
    
#     recipes_per_page = 25
#     total_pages = int(math.ceil(len(valid_recipes) / recipes_per_page))
    
#     current_page = int(request.args.get('page', 1))
  
#     start_index = (current_page - 1) * recipes_per_page
#     end_index = start_index + recipes_per_page
#     displayed_recipes = valid_recipes[start_index:end_index]

#     search_form = forms.SearchForm()  # Create an instance of the search form

#     return render_template('index.html', title='Home', recipes=displayed_recipes, form=search_form, total_pages=total_pages, current_page=current_page)   