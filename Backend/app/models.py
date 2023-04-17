from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import validates, validators

# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/  <-- One to many relationship model
# User
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(75), nullable=False, unique=True)
    phone = db.Column(db.String(12), nullable=True)
    username = db.Column(db.String(75), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    saved_recipes = db.relationship('Saved_Recipe', lazy='joined')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = generate_password_hash(kwargs.get('password'))
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<User user_id={self.id}|{self.username}>"

    def check_password(self, password_guess):
        return check_password_hash(self.password, password_guess)
    
    def as_dict(self):
        return {'user_id': self.user_id,
                'email': self.email,
                'phone': self.phone,
                'saved_recipes': self.saved_recipes}

@login.user_loader
def get_a_user_by_id(user_id):
    return db.session.get(User, user_id)


# User saved recipes
class Saved_Recipe(db.Model):
    __tablename__ = 'saved_recipes'
    saved_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_idd'))
    favorited = db.Column(db.Boolean)
    tried = db.Column(db.Boolean)
    rating = db.Column(db.Integer)
    commented = db.Column(db.String)
    
    # recipe was saved?
    recipe = db.relationship('Recipe', lazy='joined')
    # saved by whom?
    user = db.relationship('User', lazy='joined')
    
    def __repr__(self):
        return f"<User\'s selected recipes recipe={self.recipe_id} user={self.user_id} was_favorited={self.favorite}>"
    
    def as_dict(self):
        return {'saved_id': self.saved_id,
                'recipe': self.recipe,
                'recipe_id': self.recipe_id,
                'user_id': self.user_id,
                'tried': self.tried,
                'rating': self.rating,
                'favorite': self.favorited,
                'commented': self.commented,
                'user': self.user}
    
class Recipe(db.Model):
    __tablename__ = 'recipes'
    recipe_id = db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String)
    image = db.Column(db.String)
    servings = db.Column(db.Integer)
    sourceUrl = db.Column(db.String)
    cooking_mins = db.Column(db.Integer)
    prep_mins = db.Column(db.Integer)
    ready_mins = db.Column(db.Integer)
    
    # ingredients list
    ingredients = db.relationship('Recipe_Ingredient', lazy='joined')
    # # of steps to produce a recipe
    instructions = db.relationship('Instructions', lazy='joined')
    # record of number of saves by users
    saved_recipe_users = db.relationship('Saved_Recipe', lazy='joined')
    # equipment needed
    equipment = db.relationship('Equipment', lazy='joined')


    def __repr__(self):
        return f'<Recipe recipe_id={self.recipe_id} title={self.title}>'

    def as_dict(self):
        return {'recipe_id': self.recipe_id,
                'title': self.title,
                'image': self.image,
                'servings': self.servings,
                'sourceUrl': self.sourceUrl,
                'cooking_mins': self.cooking_mins,
                'prep_mins': self.prep_mins,
                'ready_mins': self.ready_mins,
                'ingredients': self.ingredients,
                'instructions': self.instructions,
                'equipment': self.equipment}
        
    @validates('image')
    def validate_image(self, key, value):
        # make sure the value is a valid URL
        assert validators.url(value), 'Image URL must be valid'
        return value        

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    name = db.Column(db.String)
    recipe_ing_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    ingredient_id = db.Column(db.Integer)
    amount = db.Column(db.Float(precision=2))
    unit = db.Column(db.String)
    description = db.Column(db.String(255))
    
    recipe = db.relationship('Recipe', lazy='joined')
    
    def __repr__(self):
        return f"<Recipe Ingredient recipe={self.recipe_id} ingredient={self.name}>"
    
    def as_dict(self):
        return {'name': self.name,
            'rec_ing_id': self.rec_ing_id,
            'recipe_id': self.recipe_id,
            'ingredient_id': self.ingredient_id,
            'amount': self.amount,
            'unit': self.unit}

class Instructions(db.Model):
    __tablename__ = 'instructions'
    instruction_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    step_num = db.Column(db.Integer)
    step_instruction = db.Column(db.String)
    
    # Instructions for these recipes
    recipe = db.relationship('Recipe', lazy='joined')

    def __repr__(self):
        return f'<Instructions recipe={self.recipe_id} step={self.step_num}>'

    def as_dict(self):
        return {'instruction_id': self.instruction_id,
                'recipe_id': self.recipe_id,
                'step_num': self.step_num,
                'step_instruction': self.step_instruction}
class Equpiment(db.Model):
    __tablename__ = 'equpiment'
    equpment_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'))
    equipment = db.Column(db.String)
    
    # Recipe the equipment correlates to
    recipe = db.relationship('Recipe', lazy='joined')
    
    def __repr__(self):
        return f'<Equipment recipe={self.recipe_id} equipment={self.equipment}>'

    def as_dict(self):
        return {'equipment_id': self.equipment_id,
                'recipe_id': self.recipe_id,
                'equipment': self.equipment}
    

def connect_to_db(flask_app, db_uri='postgresql:///recipes', echo=True):
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    flask_app.config['SQLALCHEMY_ECHO'] = echo
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.app = flask_app
    db.init_app(flask_app)
    
    print('Connection to database is established 😎')
    
if __name__ == '__main__':
    from server import app
    import os
    
    # Drop and create database (reccomended on Stackoverflow)
    os.system('dropdb recipes')
    os.system('createdb recipes')
    
    connect_to_db(app)
    # table creations
    db.create_all

