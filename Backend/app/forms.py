from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import InputRequired, EqualTo, Length


class RecipeForm(FlaskForm):
    recipe = StringField('Recipe', validators=[InputRequired()])
    search_term = StringField('Search Term')
    submit = SubmitField('Submit Address')
    

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    search_term = StringField('Search Term')
    submit = SubmitField('Log In')
    
    
class SignUpForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    email = EmailField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_pass = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    search_term = StringField('Search Term')
    submit = SubmitField('Sign Up')

class SearchForm(FlaskForm):
    search_term = StringField('Search Term')
    submit = SubmitField('Search')
    
    
class IngredientForm(FlaskForm):
    ingredient = StringField('Ingredient', validators=[InputRequired()])
    search_term = StringField('Search Term')
    submit= SubmitField('Ingredient')