from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

# TODO: Import the appropriate module for database operations
# from your_database_module import get_user_by_email, create_user

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

# Secret key (should be retrieved from env file)
SECRET_KEY = "your_secret_key"

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email and password are required!'}), 400
    
    # TODO: Check if the user already exists in the database
    # existing_user = get_user_by_email(email)
    existing_user = None  # Temporarily set to None
    if existing_user:
        return jsonify({'message': 'User already exists!'}), 400
    
    hashed_password = generate_password_hash(password, method='sha256')
    
    # TODO: Insert new user into the database
    # create_user(email, hashed_password)
    
    return jsonify({'message': 'User registered successfully!'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email and password are required!'}), 400
    
    # TODO: Retrieve the user from the database
    # user = get_user_by_email(email)
    user = None  # Temporarily set to None
    if not user or not check_password_hash("", password):  # Dummy data for password check
        return jsonify({'message': 'Invalid credentials!'}), 401
    
    token = jwt.encode({'email': email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")
    
    return jsonify({'token': token}), 200
