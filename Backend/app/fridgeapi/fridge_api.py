import requests
from dotenv import load_dotenv
import os



# define the API endpoint URL
URL = "https://api.spoonacular.com/recipes/findByIngredients"

def get_recipes(ingredients):
    # build the API request URL with the user's inputted ingredients
    params = {
        "apiKey": "dfe069817cab4c178abeed7f3b45d54f",
        "ingredients": ",".join(ingredients),
        "number": 10  # limit to 10 results
    }
    
    # make the API request and handle any errors
    try:
        response = requests.get(URL, params=params)
        response.raise_for_status()  # raise an exception for 4xx and 5xx status codes
        recipes = response.json()
        return recipes
    except requests.exceptions.HTTPError as e:
        print("HTTP error occurred:", e)
    except Exception as e:
        print("Error occurred:", e)

# example usage:
ingredients = ["chicken", "broccoli", "garlic"]
recipes = get_recipes(ingredients)
print(recipes)
