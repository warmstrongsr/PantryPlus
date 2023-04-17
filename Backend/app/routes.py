import requests 
from flask import Flask
from app import app, db
from flask import render_template, redirect, url_for, flash, session, jsonify
from app.forms import SignUpForm, LoginForm, AddressForm, SearchForm
from app.models import User, Recipe, Saved_Recipe, Ingredient, Instructions, Equpiment
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


# route decorators

@app.route('/')
def hello():
    return 'Hello World!'


@app.route('/recipes')
def get_recipes():
    url = 'https://api.spoonacular.com/recipes/random'
    params = {
        'apiKey': 'dfe069817cab4c178abeed7f3b45d54f',
        'number': 5
    }
    response = requests.get(url, params=params)
    data = response.json()
    return jsonify(data)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        search_term = form.search_term.data
        addresses = Address.query.filter((Address.first_name.ilike(f"%{search_term}%")) | (Address.last_name.ilike(f"%{search_term}%")) | (Address.phone.ilike(f"%{search_term}%")) | (Address.address.ilike(f"%{search_term}%"))).order_by(Address.last_name.asc()).all()
    else:
        addresses = Address.query.order_by(Address.last_name.asc()).all()

    return render_template('index.html', addresses=addresses, form=form)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = SearchForm()
    addresses = Address.query.filter_by(user_id=current_user.id).order_by(Address.last_name.asc()).all()
    username = current_user.username

    if form.validate_on_submit():
        search_term = form.search_term.data
        addresses = Address.query.filter((Address.first_name.ilike(f"%{search_term}%")) | (Address.last_name.ilike(f"%{search_term}%"))| (Address.phone.ilike(f"%{search_term}%")) | (Address.address.ilike(f"%{search_term}%")), Address.user_id==current_user.id).order_by(Address.last_name.asc()).all()

    return render_template('account.html', addresses=addresses, form=form, username=username)



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
def create_address():
    form = AddressForm()
    if form.validate_on_submit():
        # Get the data from the form
        first_name = form.first_name.data
        last_name = form.last_name.data
        phone = form.phone.data or None
        address = form.address.data or None
        user_id = current_user.id
        # Create an instance of Address with form data AND auth user ID
        new_address = Address(first_name=first_name, last_name=last_name, phone=phone, address=address, user_id=user_id)
        flash(f"{new_address.address} has been created!", "success")
        return redirect(url_for('account'))
    return render_template('create.html', form=form)


@app.route('/edit/<address_id>', methods=["GET", "POST"])
@login_required
def edit_address(address_id):
    form = AddressForm()
    address_to_edit = Address.query.get_or_404(address_id)
    # Make sure that the post author is the current user
    if address_to_edit.user != current_user:
        flash("You do not have permission to edit this address", "danger")
        return redirect(url_for('index'))

    # If form submitted, update Post
    if form.validate_on_submit():
        # update the post with the form data
        address_to_edit.first_name = form.first_name.data
        address_to_edit.last_name = form.last_name.data
        address_to_edit.phone = form.phone.data
        address_to_edit.address = form.address.data
        # Commit that to the database
        db.session.commit()
        flash(f"{address_to_edit.last_name, address_to_edit.first_name} has been edited!", "success")
        return redirect(url_for('account'))

    # Pre-populate the form with Address To Edit's values
    form.first_name.data = address_to_edit.first_name
    form.last_name.data = address_to_edit.last_name
    form.phone.data = address_to_edit.phone
    form.address.data = address_to_edit.address
    return render_template('edit.html', form=form, address=address_to_edit)


@app.route('/delete/<address_id>')
@login_required
def delete_address(address_id):
    address_to_delete = Address.query.get_or_404(address_id)
    if address_to_delete.user != current_user:
        flash("You do not have permission to delete this post", "danger")
        return redirect(url_for('account'))

    db.session.delete(address_to_delete)
    db.session.commit()
    flash(f"{address_to_delete.address} has been deleted", "info")
    return redirect(url_for('account'))

from flask import render_template, request
from app import app, db, login
from app.models import User, Recipe, Ingredient, Saved_Recipe

# route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # get form data and create a new user
        # ...

    # show registration form
        return render_template('register.html')

# route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get form data and log in user
        # ...

    # show login form
        return render_template('login.html')

# route for user logout
@app.route('/logout')
@login_required
def logout():
    # log out user
    # ...

    # redirect to home page
    return redirect(url_for('index'))

# route for displaying a recipe
@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    # get the recipe with the given ID
    # ...

    # show the recipe
    return render_template('recipe.html', recipe=recipe)

# route for saving a recipe
@app.route('/recipe/<int:recipe_id>/save')
@login_required
def save_recipe(recipe_id):
    # save the recipe for the logged-in user
    # ...

    # redirect to the recipe page
    return redirect(url_for('recipe', recipe_id=recipe_id))

# route for viewing saved recipes
@app.route('/saved-recipes')
@login_required
def saved_recipes():
    # get the saved recipes for the logged-in user
    # ...

    # show the saved recipes
    return render_template('saved_recipes.html', saved_recipes=saved_recipes)
