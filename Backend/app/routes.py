from app import app, db, forms, models
from flask import Flask, render_template, url_for, flash, redirect, request, abort, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc, text, func, literal, cast, String, or_
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.orm import aliased
from app.apikey import API_KEY
from app.utils import get_favorite_and_random_recipes
from app.forms import SignUpForm, LoginForm, AddRecipeForm, SearchForm
from app.models import User, Recipe, favorites, db, store_recipes,  store_database_recipes,  delete_null_title_recipes
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import math
import html
import requests, random
import json

spoonacular_api_key = API_KEY

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

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = SearchForm()
    sort_by = request.args.get('sort_by', 'title')
    order = request.args.get('title', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = 275
    username = None
    search_term = None
    total_results = 0

    valid_recipe_query = Recipe.query.filter(
        Recipe.title.isnot(None),
        Recipe.id.isnot(None),
        Recipe.image.isnot(None),
        Recipe.summary.isnot(None)
    )

    recipe_query = valid_recipe_query

    # if current_user.is_authenticated:
    #     favorite_query = valid_recipe_query.join(favorites).filter(favorites.c.user_id == current_user.id)
    #     favorite_recipes = favorite_query.order_by(favorites.c.date_favorited.desc()).all()
    #     favorite_recipe_ids = [recipe.id for recipe in favorite_recipes]
    #     other_query = valid_recipe_query.filter(~Recipe.id.in_(favorite_recipe_ids))
    #     other_recipes = other_query.order_by(text(sort_by + ' ' + order)).all()
    #     recipes = favorite_recipes + sorted(other_recipes, key=lambda x: x.title)


    # else:
    #     recipes = valid_recipe_query.order_by(text(sort_by + ' ' + order)).all()
    #     username = "None"

    pagination = None

    if form.validate_on_submit():
        search_term = form.search_term.data
        if search_term:
            recipe_query = recipe_query.filter(
                or_(
                    Recipe.title.ilike(f"%{search_term}%"),
                    Recipe.summary.ilike(f"%{search_term}%"),
                    Recipe.ingredients.ilike(f"%{search_term}%")
                )
            )
        recipes = recipe_query.order_by(Recipe.date_created.asc()).all()
        search_term = form.search_term.data

    else:
        pagination = recipe_query.paginate(page=page, per_page=per_page, error_out=False)
        recipes = pagination.items

    total_results = len(recipes)

    # for recipe in recipes:
    #     recipe.summary = recipe.summary if recipe.summary is not None else 'No summary provided'
    #     recipe.ingredients = recipe.ingredients if recipe.ingredients is not None else 'No ingredients provided'
    #     recipe.instructions = recipe.instructions if recipe.instructions is not None else 'No instructions provided'

    if request.method == 'POST':
        recipe_id = request.form.get('recipe_id')
        recipe_title = request.form.get('recipe_title', 'None')
        recipe_image = request.form.get('recipe_image')
        recipe_obj = Recipe.query.get(recipe_id)
        recipe = None

        if recipe_obj is not None:
            recipe_title = recipe_obj.title
            recipe = Recipe.query.get(recipe_id)

            if recipe is not None:
                if current_user in recipe.favorited_by:
                    # Remove the recipe from the user's favorites
                    current_user.favorites.remove(recipe)
                    db.session.commit()
                    flash(f'{recipe.title} removed from favorites.', 'danger')
                else:
                    # Add the recipe to the user's favorites
                    current_user.favorites.append(recipe)
                    db.session.commit()
                    flash(f'{recipe.title} added to favorites.', 'success')

    return render_template(
        'home.html',
        form=form,
        recipes=recipes,
        sort_by=sort_by,
        order=order,
        page=page,
        per_page=per_page,
        username=username,
        pagination=pagination,
        total_results=total_results,
        search_term=search_term
    )

import random

def get_random_recipes():
    api_key = spoonacular_api_key
    url = f"https://api.spoonacular.com/recipes/random?number=21&apiKey={api_key}"
    response = requests.get(url)
    data = json.loads(response.text)
    random_recipes = data['recipes']
    return random_recipes

@app.route('/roulette', methods=['GET', 'POST'])
@login_required
def roulette():
    page = request.args.get('page', 1, type=int)
    
    # Check the request method and handle the logic accordingly
    if request.method == 'POST':
        recipes = session.get('random_recipes', [])
    else:
        recipes = get_random_recipes()
        user_id = int(current_user.get_id())  # Get the current user's ID
        store_recipes(recipes, user_id)  # Pass the user_id to the store_recipes function
        session['random_recipes'] = recipes

    # Filter out recipes with missing data
    valid_recipes = [recipe for recipe in recipes if recipe.get('title') and recipe.get('sourceUrl')]

    # Define total pages based on number of recipes and recipes per page
    recipes_per_page = 21
    total_pages = int(math.ceil(len(valid_recipes) / recipes_per_page))

    # Get current page from query parameter or default to 1
    current_page = int(request.args.get('page', 1))

    # Slice the recipes list to show only the recipes for the current page
    start_index = (current_page - 1) * recipes_per_page
    end_index = start_index + recipes_per_page
    displayed_recipes = valid_recipes[start_index:end_index]

    search_form = forms.SearchForm()  # Create an instance of the search form

    return render_template('roulette.html', title='Home', recipes=displayed_recipes, form=search_form, total_pages=total_pages, current_page=current_page)    


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = SearchForm()
    sort_by = request.args.get('sort_by', 'title')
    order = request.args.get('order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = 30# number of items to display per page
    username = None
    recipe_image = None
    recipe_title = None
    search_term = form.search_term.data
    
    # Query User favorite recipes, excluding those with missing titles
    recipe_query = Recipe.query.join(Recipe.favorited_by).filter(User.id == current_user.id, Recipe.title != None, Recipe.image != None)


    recipe = None
    pagination = None

    if form.validate_on_submit():
        search_term = form.search_term.data
        recipes = recipe_query.filter(
            (Recipe.id.ilike(f"%{search_term}%")) |
            (Recipe.title.ilike(f"%{search_term}%")) |
            (cast(Recipe.date_created, String).ilike(f"%{search_term}%"))
        ).order_by(Recipe.date_created.asc()).all()
    else:
        pagination = recipe_query.filter(Recipe.title != None).order_by(Recipe.title.asc()).paginate(page=page, per_page=per_page, error_out=False)
        recipes = pagination.items

    if request.method == 'POST':
        recipe_id = request.form.get('recipe_id')
        recipe_title = request.form.get('recipe_title', 'None')
        recipe_image = request.form.get('recipe_image')
        recipe_obj = Recipe.query.get(recipe_id)
        recipe_link = f"https://spoonacular.com/recipes/{'-'.join(recipe_title.split(' '))}-{recipe_id}"
        recipe = None

        if recipe_obj is not None:
            recipe_title = recipe_obj.title
            recipe = Recipe.query.get(recipe_id)

        if recipe is not None:
            if current_user in recipe.favorited_by:
                # Remove the recipe from the user's favorites
                current_user.favorites.remove(recipe)
                db.session.commit()
                flash(f'{recipe.title} removed from favorites.', 'danger')
            else:
                # Add the recipe to the user's favorites
                current_user.favorites.append(recipe)
                db.session.commit()
                flash(f'{recipe.title} added to favorites.', 'success')
                
            
            # Filter out recipes with missing data
   
    return render_template('account.html', recipes=recipes, form=form, username=username, pagination=pagination,recipe=recipe,recipe_title=recipe_title, recipe_image=recipe_image, search_term=search_term, total_results=len(recipes))


@app.route('/fullmenu', methods=['GET', 'POST'])
@login_required
def fullmenu():
    form = SearchForm()
    sort_by = request.args.get('sort_by', 'title')
    order = request.args.get('order', 'asc')
    search_term = form.search_term.data
    
    # Query all recipes from the database
    recipes = Recipe.query
    
    # Exclude null recipes from page
    recipes = recipes.filter(Recipe.title.isnot(None), Recipe.image.isnot(None))

    
    # Apply the search filter if a search query is submitted
    if form.validate_on_submit():
        search_term = form.search_term.data
        recipes = recipes.filter((Recipe.id.ilike(f"%{search_term}%")) | (Recipe.title.ilike(f"%{search_term}%")) | (Recipe.date_created.ilike(f"%{search_term}%")))

    # Get the final list of recipes from the query
    recipes = recipes.all()

    user_id = int(current_user.get_id()) # Storing the current user id
    store_database_recipes(recipes, user_id)  # Pass the user_id to the store_recipes function
    
    return render_template('full_menu.html', recipes=recipes, form=form, sort_by=sort_by, order=order, total_results=len(recipes), search_term=search_term)

@app.route('/search', methods=['GET'])
def search():
    form = forms.SearchForm()
    input_value = request.args.get('search_term')
    
    if input_value:
        return redirect(url_for('results', search_term=input_value, page=1))
    return render_template('home.html', form=form, title='Home', input_value=input_value)  # Pass the form and title to the template

@app.route('/results/<search_term>/<int:page>', methods=['GET'])
def results(search_term, page=1):
    api_key = spoonacular_api_key
    results_per_page = 25 # Set the desired number of results per page
    url = f'https://api.spoonacular.com/recipes/findByIngredients?number=100&limitLicense=true&ranking=1&ignorePantry=false&ingredients={search_term}&apiKey={api_key}'
    response = requests.get(url)
    form = forms.SearchForm(default_search_term=search_term)

    if response.status_code == 200:
        all_results_data = response.json()
        offset = (page - 1) * results_per_page  # Calculate the offset based on the current page
        results_data = []

        for result in all_results_data[offset:offset+results_per_page]:
            recipe_id = result['id']
            recipe_title = result['title']
            recipe_image = result['image']
            recipe_link = f"https://spoonacular.com/recipes/{'-'.join(recipe_title.split(' '))}-{recipe_id}"
            recipe_summary = get_recipe_summary(recipe_id)
            
            # Fetch ingredients
            used_ingredients = [ingr['original'] for ingr in result.get('usedIngredients', [])]
            missed_ingredients = [ingr['original'] for ingr in result.get('missedIngredients', [])]
            all_ingredients = used_ingredients + missed_ingredients

            recipe = {'id': recipe_id, 'title': recipe_title, 'image': recipe_image, 
                    'link': recipe_link, 'summary': recipe_summary, 
                    'ingredients': all_ingredients}
            results_data.append(recipe)

        # Store the fetched recipes in the database
        if current_user.is_authenticated and current_user.is_active:
            store_recipes(results_data, current_user.id)
            print(store_database_recipes)

        total_results = len(all_results_data)  # Get the total number of results
        total_pages = math.ceil(total_results / results_per_page)
        return render_template('results.html', form=form, results=results_data, total_results=total_results, total_pages=total_pages, current_page=page, search_term=search_term)  # Return the results.html template
    else:
        flash('Error in API request')
        return redirect(url_for('login'))

@app.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    recipe_id = request.form.get('recipe_id')
    recipe = Recipe.query.get(recipe_id)

    if not recipe:
        return jsonify({'success': False})

    if current_user in recipe.favorited_users:
        # Remove the recipe from the user's favorites
        recipe.favorited_users.remove(current_user)
        is_favorite = False
    else:
        # Add the recipe to the user's favorites and set the date_favorited attribute
        recipe.favorited_users.append(current_user)
        recipe.date_favorited = datetime.utcnow()
        is_favorite = True

    db.session.commit()

    response = {
        'success': True,
        'is_favorite': is_favorite
    }
    
    return jsonify(response)



@app.route('/favorite', methods=['POST'])
def favorite():
    recipe_id = request.form.get('recipe_id')
    recipe = Recipe.query.get(recipe_id)

    if recipe and current_user.is_authenticated:
        if recipe in current_user.favorites:
            # Unfavorite the recipe
            current_user.favorites.remove(recipe)
        else:
            # Favorite the recipe
            current_user.favorites.append(recipe)
        db.session.commit()

    referrer = request.referrer
    if 'results' in referrer:
        return redirect(referrer)
    else:
        return redirect(url_for('account'))
    

@app.route('/signup', methods=["GET", "POST"])
def signup():
    # Create an instance of the form (in the context of the current request)
    form = SignUpForm()
    # Check if the form was submitted and that all of the fields are valid
    if form.validate_on_submit():
        # If so, get the data from the form fields
        print('The form has been validated.')
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        print(first_name, last_name, email, username, password)
        # Check to see if there is already a user with either username or email
        check_user = db.session.execute(db.select(User).filter((User.username == username) | (User.email == email))).scalars().all()
        if check_user:
            # Flash a message saying that user with email/username already exists
            flash("A user with that username and/or email already exists", "warning")
            return redirect(url_for('signup'))
        # If check_user is empty, create a new record in the user table
        new_user = User(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
        db.session.add(new_user)  # Add the new user to the session
        db.session.commit()  # Commit the changes to the database
        flash(f"Thank you {new_user.username} for signing up!", "success")
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print('Form Validated :)')
        username = form.username.data
        password = form.password.data
        print(username, password)
        # Check if there is a user with username and that password
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            # If the user exists and has the correct password, log them in
            login_user(user)
            flash(f'You have successfully logged in as {username}', 'success')
            return redirect(url_for('account'))
        else:
            flash('Invalid username and/or password. Please try again', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have logged out", "info")
    return redirect(url_for('home'))


#****DELETE****DELETE***DELETE*****
# Delete a recipe from the database
@app.route('/delete_null_recipes', methods=['POST'])
@login_required
def delete_null_recipes():
    null_recipes = Recipe.query.filter((Recipe.title.is_(None)) | (Recipe.image.is_(None))).all()
    for recipe in null_recipes:
        db.session.delete(recipe)
    db.session.commit()
    flash(f"Null recipes have been deleted", "info")
    return redirect(url_for('fullmenu'))


@app.route('/recipe')
def recipe():
  recipe = Recipe.query.all() # replace this with however you're getting the recipe
  return render_template('recipe.html', recipe=recipe)


@app.route('/recipes')
def list_recipes():
    recipes = Recipe.query.all()
    for recipe in recipes:
        recipe.ingredients = json.loads(recipe.ingredients)
    return render_template('recipes.html', recipes=recipes)


# @app.route('/recipes')
# def list_recipes():
#     recipes = Recipe.query.all()
#     for recipe in recipes:
#         recipe_ingredients = json.dumps(recipe.ingredients)
#     return render_template('recipes.html', recipes=recipes)

# def get_recipe_data(recipe_id):
#     api_key = '<your_spoonacular_api_key>'
#     url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=false&apiKey={api_key}'
#     response = requests.get(url)
#     if response.status_code == 200:
#         recipe_data = response.json()
#         return recipe_data
#     else:
#         return None



    # recipes = []
    # for recipe in data['recipes']:
    #     recipe_id = recipe['id']
    #     recipe_title = recipe['title']
    #     recipe_image = recipe['image']
    #     recipe_link = recipe['sourceUrl']
    #     recipe_instructions = ' '.join([step['step'] for step in recipe['analyzedInstructions'][0]['steps']]) if recipe['analyzedInstructions'] else ''
    #     recipe_summary = recipe['summary']
    #     recipe_data = {
    #         'id': recipe_id,
    #         'title': recipe_title,
    #         'image': recipe_image,
    #         'sourceUrl': recipe_link,
    #         'instructions': recipe_instructions,
    #         'summary': recipe_summary
    #     }
    #     recipes.append(recipe_data)

    # return recipes

    


# def get_random_recipes():
#     api_key = spoonacular_api_key
#     url = f"https://api.spoonacular.com/recipes/random?number=50&apiKey={api_key}"
#     response = requests.get(url)
#     data = json.loads(response.text)
#     random_recipes = data['recipes']
#     return random_recipes

def get_recipe_summary(recipe_id):
    api_key = spoonacular_api_key
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/summary?apiKey={api_key}"
    response = requests.get(url)
    data = json.loads(response.text)
    recipe_summary = data['summary']
    return recipe_summary



