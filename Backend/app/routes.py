import os
import requests
from dotenv import load_dotenv
from pprint import pprint
from app import app, db, login
from flask import (Flask, render_template, redirect, url_for, flash, session, jsonify, request)
from app.models import User, Recipe, Saved_Recipe, Ingredient, Instructions, Equpiment
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User
load_dotenv()


@app.route('/')
def hello():
    return 'Hello World!'


# route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # get form data and create a new user
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:
            # check if user with the given username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already taken. Please choose a different username.')
                return redirect(url_for('register'))

            # create a new user
            new_user = User(username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))
        else:
            flash('Please provide both username and password.')
            return redirect(url_for('register'))

    # show registration form
    return render_template('register.html')

# route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
       # get form data and log in user
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:
            # find user with the given username
            user = User.query.filter_by(username=username).first()

            # check if user exists and password is correct
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash('Logged in successfully.')
                return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    # show login form
    return render_template('login.html')
# route for user logout
@app.route('/logout')
@login_required
def logout():
    # log out user
    logout_user()
    # redirect to home page
    return redirect(url_for('index'))

# route for displaying a recipe
@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    # get the recipe with the given ID
    recipe = Recipe.query.get(recipe_id)
    # show the recipe
    return render_template('recipe.html', recipe=recipe)

# Saving a recipe route
@app.route('/recipe/<int:recipe_id>/save')
@login_required
def save_recipe(recipe_id):
    # save the recipe for the user
    recipe = Recipe.query.get(recipe_id)
    #create a new saved recipe and add it to the user's list (saved recipes)
    saved_recipe = Saved_Recipe(user=current_user, recipe=recipe)
    db.session.add(saved_recipe)
    db.session.commit()
    # redirect to the recipe page
    return redirect(url_for('recipe', recipe_id=recipe_id))

# Viewing the saved recipes route
@app.route('/saved-recipes')
@login_required
def saved_recipes():
    # get the saved recipes for user
    saved_recipes = Saved_Recipe.query.filter_by(recipe_id=current_user.id).all()
    # show the recipes that were saved
    return render_template('saved_recipes.html', saved_recipes=saved_recipes)

