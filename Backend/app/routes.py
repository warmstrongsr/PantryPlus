from app import app, db, forms, models
from app.dummy_recipes import dummy_recipes
from flask import render_template, redirect, url_for, flash, request
from app.apikey import API_KEY
from app.forms import SignUpForm, LoginForm, AddRecipeForm, SearchForm
from app.models import User, Recipe, favorites, db
from math import ceil
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import requests, random
import json

spoonacular_api_key = API_KEY

from app import routes


@app.route('/', methods=['GET', 'POST'])
def index():
    search_form = SearchForm()
    recipes = Recipe.query.all()
    # Filter out recipes with missing data
    valid_recipes = [recipe for recipe in recipes if recipe.title and recipe.link]
    # Convert valid recipes to dictionaries
    recipes_data = [recipe.to_dict(current_user) for recipe in valid_recipes]

    # Combine fetched recipes and dummy data
    all_recipes = recipes_data + dummy_recipes

    # Fetch random recipes
    api_key = spoonacular_api_key
    url = f"https://api.spoonacular.com/recipes/random?number=40&apiKey={api_key}"
    response = requests.get(url)
    data = json.loads(response.text)
    random_recipes = data['recipes']
    # Combine random recipes with existing recipes
    all_recipes = recipes_data + random_recipes
        
    return render_template('index.html', title='Home', recipes=all_recipes, form=search_form)




@app.route('/search', methods=['GET'])
def search():
    form = forms.SearchForm()
    input_value = request.args.get('search_term')
    
    if input_value:
        return redirect(url_for('results', search_term=input_value, page=1))
    return render_template('index.html', form=form)


@app.route('/results/<search_term>/<int:page>', methods=['GET'])
def results(search_term, page=1):
    api_key = spoonacular_api_key
    results_per_page = 15  # Set the desired number of results per page
    url = f'https://api.spoonacular.com/recipes/findByIngredients?number=45&limitLicense=true&ranking=1&ignorePantry=false&ingredients={search_term}&apiKey={api_key}'
    response = requests.get(url)
    form = forms.SearchForm()

    if response.status_code == 200:
        all_results_data = response.json()
        offset = (page - 1) * results_per_page  # Calculate the offset based on the current page
        results_data = all_results_data[offset:offset+results_per_page]
        total_results = len(all_results_data)  # Get the total number of results
        total_pages = ceil(total_results / results_per_page)
        return render_template('results.html', input_value=search_term, results=results_data, form=form, current_page=page, total_pages=total_pages)
    else:
        flash('Error in API request')
        return redirect(url_for('results'))

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


@app.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    recipe_id = request.form.get('recipe_id')
    recipe_title = request.form.get('recipe_title')
    recipe_image = request.form.get('recipe_image')
    recipe = Recipe.query.get(recipe_id)

    if not recipe:
        recipe = Recipe(id=recipe_id, title=recipe_title, image=recipe_image, user_id=current_user.id)
        db.session.add(recipe)
        db.session.commit()

    if current_user in recipe.favorited_by.all():
        # Remove the recipe from the user's favorites
        current_user.favorites.remove(recipe)
        if current_user in recipe.latest_users.all():  # Check if the relationship exists
            recipe.latest_users.remove(current_user)
        db.session.commit()
        flash(f'{recipe.title} removed from favorites.', 'danger')
    else:
        # Add the recipe to the user's favorites
        current_user.favorites.append(recipe)
        recipe.latest_users.append(current_user)
        if len(recipe.latest_users.all()) > 3:
            oldest_user = min(recipe.latest_users, key=lambda user: user.latest_added_recipes.filter_by(id=recipe.id).first().timestamp)
            recipe.latest_users.remove(oldest_user)
        db.session.commit()
        flash(f'{ recipe.title} added to favorites.', 'success')

    # Always redirect to account page
    return redirect(url_for('account'))

@app.route('/random_recipes')
def random_recipes():
    api_key = "YOUR_SPOONACULAR_API_KEY"
    url = f"https://api.spoonacular.com/recipes/random?number=20&apiKey={api_key}"
    response = requests.get(url)
    data = json.loads(response.text)
    recipes = data['recipes']
    return render_template('index.html', recipes=recipes)


@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = AddRecipeForm()
    if form.validate_on_submit():
        recipe = Recipe(title=form.title.data, link=form.link.data, image=form.image.data, user_id=current_user.id)
        flash('Recipe added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_recipe.html', title='Add Recipe', form=form)



@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = SearchForm()
    recipes = Recipe.query.filter_by(user_id=current_user.id).order_by(Recipe.title.asc()).all()
    username = current_user.username

    if form.validate_on_submit():
        search_term = form.search_term.data
        recipes = Recipe.query.filter((Recipe.id.ilike(f"%{search_term}%")) | (Recipe.title.ilike(f"%{search_term}%")) | (Recipe.date_created.ilike(f"%{search_term}%")), Recipe.user_id==current_user.id).order_by(Recipe.user_id.asc()).all()

    return render_template('account.html', recipes=recipes, form=form, username=username)



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


# Delete a recipe from the database
@app.route('/delete/<recipe_id>')
@login_required
def delete_recipe(recipe_id):
    recipe_to_delete = Recipe.query.get_or_404(recipe_id)
    if recipe_to_delete.user != current_user:
        flash("You do not have permission to delete this post", "danger")
        return redirect(url_for('account'))

    db.session.delete(recipe_to_delete)
    db.session.commit()
    flash(f"{recipe_to_delete.title} has been deleted", "info")
    return redirect(url_for('account'))





    
    
