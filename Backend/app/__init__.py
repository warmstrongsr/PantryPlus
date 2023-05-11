from flask import Flask
# Import the Config class from the config module that has the app configurations like SECRET_KEY, etc
from config import Config
import json







# Import the classes from Flask-SQLAlchemy and Flask-Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
# set optional bootswatch theme
# app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

# Add administrative views here
# Flask and Flask-SQLAlchemy initialization here
# admin = Admin(app, name='microblog', template_mode='bootstrap3')
# admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(Post, db.session))
# app.run()

# Create an instance of SQLAlchemy to connect our app to the database

db = SQLAlchemy(app)
# Create an instance of Migrate that will track our db and app
migrate = Migrate(app, db)

# Create an instance of the LoginManager to set up Authentication
login = LoginManager(app)
# Tell the login manager where to redirect if a user is not logged in
login.login_view = 'login'
# login.login_message = "Invalid Option."
login.login_message_category = 'danger'
# bcrypt = Bcrypt(app)

# import all of the routes from the routes file and models from the models file into the current package
from app import routes, models

def json_loads(value):
    if value is None or value.strip() == '':
        return None
    return json.loads(value)

app.jinja_env.filters['json_loads'] = json_loads


app.jinja_env.filters['json_loads'] = json_loads

