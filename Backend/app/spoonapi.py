import os
from spoonacular import SpoonacularAPI
from app.models import Recipe, Ingredient, Recipe_Ingredient

# create an instance of the SpoonacularAPI class
spoon = SpoonacularAPI(API_KEY)

# make a request to the Spoonacular API to get recipe information
response = spoon.search_recipes_by_ingredients(ingredients='chicken, broccoli, rice', number=10)

# iterate through the response and create Recipe, Ingredient, and Recipe_Ingredient objects
for result in response['results']:
    # create a new Recipe object
    recipe = Recipe(title=result['title'], servings=result['servings'], sourceUrl=result['sourceUrl'])
    
    # create a new Ingredient object for each ingredient in the recipe
    for ingredient in result['usedIngredients'] + result['missedIngredients']:
        ingredient_obj = Ingredient(name=ingredient['name'])
        
        # create a new Recipe_Ingredient object to link the Recipe and Ingredient objects
        recipe_ingredient = Recipe_Ingredient(recipe=recipe, ingredient=ingredient_obj, quantity=ingredient['amount'])
        
        # add the Recipe, Ingredient, and Recipe_Ingredient objects to the session
        db.session.add(recipe)
        db.session.add(ingredient_obj)
        db.session.add(recipe_ingredient)
    
# commit the changes to the database
db.session.commit()
