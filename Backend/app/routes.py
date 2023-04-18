from flask import jsonify, request
from app.blueprints.api import api
from app.blueprints.api.models import Post, User
from app.blueprints.api.http_auth import basic_auth, token_auth


# Login - Get Token with Username/Password in header
@api.route('/token', methods=['POST'])
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    token = user.get_token()
    return jsonify({'token': token})


# Create a user
@api.route('/users', methods=['POST'])
def create_user():
    data = request.json
    # Validate the data
    for field in ['username', 'email', 'password']:
        if field not in data:
            return jsonify({'error': f"You are missing the {field} field"}), 400

    # Grab the data from the request body
    username = data['username']
    email = data['email']

    # Check if the username or email already exists
    user_exists = User.query.filter((User.username == username)|(User.email == email)).all()
    # if it is, return back to register
    if user_exists:
        return jsonify({'error': f"User with username {username} or email {email} already exists"}), 400

    # Create the new user
    # new_user = User(username=username, email=email, password=password)
    new_user = User(**data)

    return jsonify(new_user.to_dict())


# Update a user by id 
@api.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def updated_user(id):
    current_user = token_auth.current_user()
    if current_user.id != id:
        return jsonify({'error': 'You do not have access to update this user'}), 403
    user = User.query.get_or_404(id)
    data = request.json
    user.update(data)
    return jsonify(user.to_dict())


# Delete a user by id
@api.route('/users/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_user(id):
    current_user = token_auth.current_user()
    if current_user.id != id:
        return jsonify({'error': 'You do not have access to delete this user'}), 403
    user_to_delete = User.query.get_or_404(id)
    user_to_delete.delete()
    return jsonify({'success': f'{user_to_delete.username} has been deleted'})


# Get user info from token
@api.route('/me')
@token_auth.login_required
def me():
    return token_auth.current_user().to_dict()


# Create a blog post
@api.route('/posts', methods=['POST'])
@token_auth.login_required
def create_post():
    if not request.is_json:
        return jsonify({'error': 'Please send a body'}), 400
    data = request.json
    # Validate the data
    for field in ['title', 'content']:
        if field not in data:
            return jsonify({'error': f"You are missing the {field} field"}), 400
    current_user = token_auth.current_user()
    data['user_id'] = current_user.id
    new_post = Post(**data)
    return jsonify(new_post.to_dict()), 201


# Get all posts
@api.route('/posts')
def get_posts():
    posts = Post.query.all()
    return jsonify([p.to_dict() for p in posts])


# Get a single post with id
@api.route('/posts/<int:post_id>')
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict())


# Update a single post with id
@api.route('/posts/<int:post_id>', methods=['PUT'])
@token_auth.login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    user = token_auth.current_user()
    if user.id != post.user_id:
        return jsonify({'error': 'You are not allowed to edit this post'}), 403
    data = request.json
    post.update(data)
    return jsonify(post.to_dict())


# Delete a single post with id
@api.route('/posts/<int:post_id>', methods=['DELETE'])
@token_auth.login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    user = token_auth.current_user()
    if user.id != post.user_id:
        return jsonify({'error': 'You are not allowed to edit this post'}), 403
    post.delete()
    return jsonify({'success': f'{post.title} has been deleted'})