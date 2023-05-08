from app import app, db, forms, models
from app.dummy_recipes import dummy_recipes
from flask import Flask, render_template, url_for, flash, redirect, request, abort, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc, text, func, literal
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app.apikey import API_KEY
from app.forms import SignUpForm, LoginForm, AddRecipeForm, SearchForm
from app.models import User, Recipe, favorites, db, store_recipes, delete_null_title_recipes
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import math
import requests, random
import json


spoonacular_api_key = API_KEY


def get_random_recipes():
    num_recipes = 100 # number of random recipes to retrieve
    random_recipes = Recipe.query.order_by(func.random()).limit(num_recipes).all()
    return random_recipes


def get_random_recipes():
    api_key = spoonacular_api_key
    url = f"https://api.spoonacular.com/recipes/random?number=100&apiKey={api_key}"
    response = requests.get(url)
    data = json.loads(response.text)
    random_recipes = data['recipes']
    return random_recipes

def get_recipe_summary(recipe_id):
    api_key = spoonacular_api_key
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/summary?apiKey={api_key}"
    response = requests.get(url)
    data = json.loads(response.text)
    recipe_summary = data['summary']
    return recipe_summary



@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = SearchForm()
    sort_by = request.args.get('sort_by', 'title')
    order = request.args.get('order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = 150
    username = None
    
    # initialize the variable outside of any conditional branches
    recipe_query = Recipe.query
    
    if current_user.is_authenticated:
        subquery = db.session.query(
        Recipe.id.label('recipe_id'),
        (Recipe.favorited_by.contains(current_user).label('is_favorited')),
        literal(current_user.id).label('user_id')
    ).subquery()
        username = current_user.username

        recipe_query = recipe_query.join(subquery, Recipe.id == subquery.c.recipe_id).filter_by(user_id=current_user.id).order_by(
            subquery.c.is_favorited.desc(),
            text(sort_by + ' ' + order))
    else:
        recipe_query = Recipe.query
        username = "None"

        
    # update the 'recipes' variable with the new query
    recipes = recipe_query.paginate(page=page, per_page= 5, error_out=False).items
    
    # Filter out recipes with missing data
    valid_recipes = [recipe for recipe in recipes if isinstance(recipe, Recipe) and 'title' in recipe.to_dict() and 'sourceUrl' in recipe.to_dict()]
    total_pages = int(math.ceil(len(valid_recipes) / per_page))
   
    # Apply the search filter if a search query is submitted
    if form.validate_on_submit():
        search_term = form.search_term.data
        
        if current_user.is_authenticated:
            recipe_query = Recipe.query.filter_by(user_id=current_user.id).filter(
                (Recipe.id.ilike(f"%{search_term}%")) |
                (Recipe.title.ilike(f"%{search_term}%"))
            ).order_by(
                db.case((Recipe.favorited_by.contains(current_user), 0), else_=1),
                text(sort_by + ' ' + order))
        else:
            recipe_query = Recipe.query.filter(
                (Recipe.id.ilike(f"%{search_term}%")) |
                (Recipe.title.ilike(f"%{search_term}%"))
            ).order_by(Recipe.title.desc())
        
        recipes = recipe_query.paginate(page=page, per_page= 5, error_out=False).items
    
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
            if current_user.is_authenticated and current_user in recipe.favorited_by:
                # Remove the recipe from the user's favorites
                current_user.favorites.remove(recipe)
                db.session.commit()
                flash(f'{recipe.title} removed from favorites.', 'danger')
            elif current_user.is_authenticated:
                # Add the recipe to the user's favorites
                current_user.favorites.append(recipe)
                db.session.commit()
                flash(f'{recipe.title} added to favorites.', 'success')
            else:
                flash("You need to login to add recipes to your favorites.", 'danger')

        recipes_per_page = 25
        total_pages = int(math.ceil(len(valid_recipes) / recipes_per_page))

        # Get current page from query parameter or default to 1
        current_page = int(request.args.get('page', 1))

        # Add dummy recipes to the valid recipes list if it's the last page
        if current_page == total_pages:
            valid_recipes += dummy_recipes

        # Slice the recipes list to show only the recipes for the current page
        start_index = (current_page - 1) * recipes_per_page
        end_index = start_index + recipes_per_page
        displayed_recipes = valid_recipes[start_index:end_index]

        search_form = forms.SearchForm()  # Create an instance of the search form
            

    return render_template('home.html', form=form, recipes=recipes, sort_by=sort_by, order=order, page=page,per_page=per_page, total_pages=total_pages, username=username)
        
    
    
    
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
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
    recipes_per_page = 1
    total_pages = int(math.ceil(len(valid_recipes) / recipes_per_page))

    # Get current page from query parameter or default to 1
    current_page = int(request.args.get('page', 1))

    # Add dummy recipes to the valid recipes list if it's the last page
    if current_page == total_pages:
        valid_recipes += dummy_recipes

    # Slice the recipes list to show only the recipes for the current page
    start_index = (current_page - 1) * recipes_per_page
    end_index = start_index + recipes_per_page
    displayed_recipes = valid_recipes[start_index:end_index]

    search_form = forms.SearchForm()  # Create an instance of the search form

    return render_template('index.html', title='Home', recipes=displayed_recipes, form=search_form, total_pages=total_pages, current_page=current_page)    


@app.route('/fullmenu', methods=['GET', 'POST'])
@login_required
def fullmenu():
    form = SearchForm()
    sort_by = request.args.get('sort_by', 'title')
    order = request.args.get('order', 'asc')
    
    # Query all recipes from the database
    recipes = Recipe.query
    
    # Apply the search filter if a search query is submitted
    if form.validate_on_submit():
        search_term = form.search_term.data
        recipes = recipes.filter((Recipe.id.ilike(f"%{search_term}%")) | (Recipe.title.ilike(f"%{search_term}%")) | (Recipe.date_created.ilike(f"%{search_term}%")))

    # Get the final list of recipes from the query
    recipes = recipes.all()

    return render_template('full_menu.html', recipes=recipes, form=form, sort_by=sort_by, order=order)


@app.route('/search', methods=['GET'])
def search():
    form = forms.SearchForm()
    input_value = request.args.get('search_term')
    
    if input_value:
        return redirect(url_for('results', search_term=input_value, page=1))
    return render_template('index.html', form=form, title='Home', input_value=input_value)  # Pass the form and title to the template

@app.route('/results/<search_term>/<int:page>', methods=['GET'])
def results(search_term, page=1):
    api_key = spoonacular_api_key
    results_per_page = 35  # Set the desired number of results per page
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
            recipe = {'id': recipe_id, 'title': recipe_title, 'image': recipe_image, 'link': recipe_link, 'summary': recipe_summary}
            results_data.append(recipe)

        total_results = len(all_results_data)  # Get the total number of results
        total_pages = math.ceil(total_results / results_per_page)
        return render_template('results.html', form=form, results=results_data, total_pages=total_pages, current_page=page, search_term=search_term)  # Return the results.html template
    else:
        flash('Error in API request')
        return redirect(url_for('index'))

@login_required
@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    recipe_id = request.form.get('recipe_id')
    recipe_title = request.form.get('recipe_title')
    recipe_image = request.form.get('recipe_image')
    recipe = Recipe.query.get(recipe_id)

    if not recipe:
        recipe = Recipe(id=recipe_id, title=recipe_title, image=recipe_image)
        db.session.add(recipe)

    if current_user in recipe.favorited_users:
        # Remove the recipe from the user's favorites
        recipe.favorited_users.remove(current_user)
        flash(f'{recipe.title} {recipe.id} removed from favorites.', 'danger')
    else:
        # Add the recipe to the user's favorites and set the date_favorited attribute
        recipe.favorited_users.append(current_user)
        recipe.date_favorited = datetime.utcnow()
        flash(f'{recipe.title} {recipe.id} added to favorites.', 'success')

    db.session.commit()

    # Get the previous page URL from the request referrer
    prev_page = request.referrer
    if prev_page:
        # Check if the previous page URL contains 'favorites' or 'results'
        if 'favorites' in prev_page:
            return redirect(url_for('account', _method='POST', _external=True))
        elif 'results' in prev_page:
            # Extract the search_term and page from the previous page URL
            parsed_url = urlparse(prev_page)
            search_term = parse_qs(parsed_url.query).get('search_term', [''])[0]
            page = parse_qs(parsed_url.query).get('page', [1])[0]
            return redirect(url_for('account', search_term=search_term, page=page, _external=True))
    # If the previous page URL is not available, redirect to the index page
    return redirect(url_for('account', _method='POST', _external=True))




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
    



# @app.route('/add_recipe', methods=['GET', 'POST'])
# @login_required
# def add_recipe():
#     form = AddRecipeForm()
#     if form.validate_on_submit():
#         recipe = Recipe(title=form.title.data, link=form.link.data, image=form.image.data, user_id=current_user.id)
#         flash('Recipe added successfully!', 'success')
#         return redirect(url_for('index'))
#     return render_template('add_recipe.html', title='Add Recipe', form=form)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = SearchForm()
    username = current_user.username
    current_page = request.args.get('page', 1, type=int)
    per_page = 25  #page calculations and parameters
    total_recipes = Recipe.query.filter_by(user_id=current_user.id).count()
    total_pages = int(math.ceil(total_recipes / per_page)) 

    if form.validate_on_submit():
        search_term = form.search_term.data
        recipes = Recipe.query.filter_by(user_id=current_user.id).filter(
            (Recipe.id.ilike(f"%{search_term}%")) |
            (Recipe.title.ilike(f"%{search_term}%")) |
            (Recipe.date_created.ilike(f"%{search_term}%"))
        ).order_by(Recipe.date_created.asc()).all()
    else:
        recipes = Recipe.query.filter_by(user_id=current_user.id).filter(
            Recipe.title != None
        ).order_by(Recipe.date_created.desc()).all()

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
            
            # Filter out recipes with missing data
   

    return render_template('account.html',current_page=current_page, recipes=recipes, form=form, username=username, total_pages=total_pages)



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
    return redirect(url_for('index'))

#****DELETE****DELETE***DELETE*****
# Delete a recipe from the database
@app.route('/delete/<recipe_id>')
@login_required
def delete_recipe(recipe_id):
    # Null deletions
    delete_null_title_recipes()
    recipe_to_delete = Recipe.query.get_or_404(recipe_id)
    if recipe_to_delete.user != current_user:
        flash("You do not have permission to delete this post", "danger")
        return redirect(url_for('login'))
    # Delete the recipe
    db.session.delete(recipe_to_delete)
    db.session.commit()
    flash(f"{recipe_to_delete.title} has been deleted", "info")
    return redirect(url_for('account'))
