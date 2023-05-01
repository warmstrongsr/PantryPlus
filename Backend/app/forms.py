from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import InputRequired, EqualTo, Length, DataRequired


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
    search_term = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        if 'default_search_term' in kwargs:
            self.search_term.data = kwargs['default_search_term']


    
    
class IngredientForm(FlaskForm):
    ingredient = StringField('Ingredient', validators=[InputRequired()])
    search_term = StringField('Search Term')
    submit= SubmitField('Ingredient')
    
class AddRecipeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    link = StringField('Link', validators=[DataRequired()])
    image = StringField('Image URL')
    submit = SubmitField('Add Recipe')