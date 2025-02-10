from flask import Blueprint, request, jsonify
import jwt
import datetime
import bcrypt
from database import db

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = "secret"
users_collection = db["users"]

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'message': 'Kullanıcı adı, e-posta ve şifre gereklidir!'}), 400

    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return jsonify({'message': 'Bu e-posta adresi ile kayıtlı bir kullanıcı zaten var!'}), 400

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    user_data = {
        "username": username,
        "email": email,
        "password": hashed_password.decode('utf-8'),
        "salt": salt.decode('utf-8')
    }
    users_collection.insert_one(user_data)

    return jsonify({'message': 'Kullanıcı başarıyla kaydedildi!'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'E-posta ve şifre gereklidir!'}), 400
    
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({'message': 'Geçersiz e-posta veya şifre!'}), 401

    stored_salt = user["salt"].encode('utf-8')
    stored_hashed_password = user["password"].encode('utf-8')

    hashed_input_password = bcrypt.hashpw(password.encode('utf-8'), stored_salt)

    if hashed_input_password != stored_hashed_password:
        return jsonify({'message': 'Geçersiz e-posta veya şifre!'}), 401

    token = jwt.encode(
        {'email': email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
        SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({'token': token}), 200
