from app import app, forms, db
from flask import render_template, redirect, url_for, flash, jsonify, request

# from fake_data import posts
from app.forms import SignUpForm, LoginForm, RecipeForm, SearchForm
from app.models import User, Recipe
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import requests
import os
import sys
API_KEY = "dfe069817cab4c178abeed7f3b45d54f"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))






from app import routes, models

@app.route('/')
def index():
    form = forms.SearchForm()
    return render_template('index.html', form=form)

@app.route('/', methods=['POST'])
def search():
    form = forms.SearchForm()
    if form.validate_on_submit():
        input_value = form.search_term.data
        return render_template('results.html', input_value=input_value)
    return redirect(url_for('index'))


# @app.route('/search', methods=['GET', 'POST'])
# def search():
#     form = SearchForm()
#     if form.validate_on_submit():
#         input_value = form.search_term.data
#         # Query the database to get search results
#         results = db.session.query(Item).filter(Item.name.like(f'%{input_value}%')).all()
#         return render_template('index.html', form=form, results=results)
#     return render_template('index.html', form=form)




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


@app.route('/create', methods=["GET", "POST"])
@login_required
def create_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        # Get the data from the form
        first_name = form.first_name.data
        last_name = form.last_name.data
        phone = form.phone.data or None
        recipe = form.recipe.data or None
        user_id = current_user.id
        # Create an instance of Recipe with form data AND auth user ID
        new_recipe = Recipe(first_name=first_name, last_name=last_name, phone=phone, recipe=recipe, user_id=user_id)
        flash(f"{new_recipe.recipe} has been created!", "success")
        return redirect(url_for('account'))
    return render_template('create.html', form=form)


@app.route('/edit/<recipe_id>', methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    form = RecipeForm()
    recipe_to_edit = Recipe.query.get_or_404(recipe_id)
    # Make sure that the post author is the current user
    if recipe_to_edit.user != current_user:
        flash("You do not have permission to edit this recipe", "danger")
        return redirect(url_for('index'))

    # If form submitted, update Post
    if form.validate_on_submit():
        # update the post with the form data
        recipe_to_edit.first_name = form.first_name.data
        recipe_to_edit.last_name = form.last_name.data
        recipe_to_edit.phone = form.phone.data
        recipe_to_edit.recipe = form.recipe.data
        # Commit that to the database
        db.session.commit()
        flash(f"{recipe_to_edit.last_name, recipe_to_edit.first_name} has been edited!", "success")
        return redirect(url_for('account'))

    # Pre-populate the form with Recipe To Edit's values
    form.first_name.data = recipe_to_edit.first_name
    form.last_name.data = recipe_to_edit.last_name
    form.phone.data = recipe_to_edit.phone
    form.recipe.data = recipe_to_edit.recipe
    return render_template('edit.html', form=form, recipe=recipe_to_edit)


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




# @app.route('/', methods=['GET', 'POST'])
# def index():
#     form = SearchForm()
#     if form.validate_on_submit():
#         search_term = form.search_term.data
#         recipes = Recipe.query.filter((Recipe.first_name.ilike(f"%{search_term}%")) | (Recipe.last_name.ilike(f"%{search_term}%")) | (Recipe.phone.ilike(f"%{search_term}%")) | (Recipe.recipe.ilike(f"%{search_term}%"))).order_by(Recipe.last_name.asc()).all()
#     else:
#         recipes = Recipe.query.order_by(Recipe.last_name.asc()).all()

    # return render_template('index.html', recipes=recipes, form=form)
    
    
    
    
if __name__ == '__main__':
    app.run(debug=True)