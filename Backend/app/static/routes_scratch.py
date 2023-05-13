# from flask import redirect, url_for

# @login_required
# @app.route('/toggle_favorite', methods=['POST'])
# def toggle_favorite():
#     recipe_id = request.form.get('recipe_id')
#     recipe_title = request.form.get('recipe_title')
#     recipe_image = request.form.get('recipe_image')
#     recipe = Recipe.query.get(recipe_id)
    

#     if not recipe:
#         recipe = Recipe(id=recipe_id, title=recipe_title, image=recipe_image)
#         db.session.add(recipe)

#     if current_user in recipe.favorited_users:
#         # Remove the recipe from the user's favorites
#         recipe.favorited_users.remove(current_user)
#         flash(f'{recipe.title} {recipe.id} removed from favorites.', 'danger')
#     else:
#         # Add the recipe to the user's favorites and set the date_favorited attribute
#         recipe.favorited_users.append(current_user)
#         recipe.date_favorited = datetime.utcnow()
#         flash(f'{recipe.title} {recipe.id} added to favorites.', 'success')

#     db.session.commit()
    
#     search_term = session.get('search_term', '')
#     page = session.get('page', 1)
#     # Get the previous page URL from the request referrer
#     prev_page = request.referrer
#     if prev_page:
#         if 'account' in prev_page:
#             return redirect(url_for('account', _external=True))
#         elif 'results' in prev_page:
#             parsed_url = urlparse(prev_page)
#             search_term = parse_qs(parsed_url.query).get('search_term', [''])[0]
#             page = parse_qs(parsed_url.query).get('page', [1])[0]
#             return redirect(url_for('results', search_term=search_term, page=page, _external=True))
#         elif 'home' in prev_page:
#             return redirect(url_for('home', _external=True))
#         elif 'fullmenu' in prev_page:
#             return redirect(url_for('fullmenu', _external=True))
#     # If the previous page URL is not available or is not recognized, redirect to the account page
#     return redirect(url_for('account', _external=True))