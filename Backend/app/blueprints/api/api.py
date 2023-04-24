import requests


def formatMethodName(name):
    name = name.lower().replace('(', '').replace(')', '')
    return name.replace(' ', '_')


class API(object):
    """Spoonacular API"""

  
    session = requests.Session()
    session.headers = {"Application": "spoonacular",
                       "Content-Type": "application/x-www-form-urlencoded"}

    def search_recipes_by_ingredients(self, ingredients, fillIngredients=None, limitLicense=None, number=None, ranking=None):
        """ Find recipes that use as many of the given ingredients
            as possible and have as little as possible missing
            ingredients. This is a whats in your fridge API endpoint.
            https://spoonacular.com/food-api/docs#search-recipes-by-ingredients
        """
        endpoint = "recipes/findByIngredients"
        url_query = {}
        url_params = {"fillIngredients": fillIngredients, "ingredients": ingredients, "limitLicense": limitLicense, "number": number, "ranking": ranking}
        return self._make_request(endpoint, method="GET", query_=url_query, params_=url_params)
