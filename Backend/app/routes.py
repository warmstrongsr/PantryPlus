from app import app, db, forms, models
from flask import render_template, redirect, url_for, flash, request
from app.apikey import API_KEY
from app.forms import SignUpForm, LoginForm, RecipeForm, SearchForm
from app.models import User, Recipe, favorites, db
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import requests, random
from math import ceil

spoonacular_api_key = API_KEY

from app import routes

@app.route('/', methods=['GET', 'POST'])
def index():
    form = forms.SearchForm()
    if form.validate_on_submit():
        input_value = form.search_term.data
        return redirect(url_for('search', search_term=input_value))
    recipes = models.Recipe.query.all()
    return render_template('index.html', form=form, recipes=recipes)

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
    url = f'https://api.spoonacular.com/recipes/findByIngredients?number=50&limitLicense=true&ranking=1&ignorePantry=false&ingredients={search_term}&apiKey={api_key}'
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
        return redirect(url_for('index'))

@app.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    recipe_id = request.form.get('recipe_id')
    recipe = Recipe.query.get(recipe_id)
    
    if not recipe:
        # If the recipe is not in the database, create it/save
        recipe = Recipe(id=recipe_id, title=request.form.get('recipe_title'), user_id=current_user.id)
        db.session.add(recipe)
        db.session.commit()

    if current_user in recipe.favorited_by.all():
        # Remove the recipe from the user's favorites
        current_user.favorites.remove(recipe)
        db.session.commit()
        flash('Recipe removed from favorites.', 'success')
    else:
        # Add the recipe to the user's favorites
        current_user.favorites.append(recipe)
        db.session.commit()
        flash('Recipe added to favorites.', 'success')

    return redirect(request.referrer or url_for('index'))



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
    flash(f"{recipe_to_delete.recipe} has been deleted", "info")
    return redirect(url_for('account'))





    
    
