from flask import Blueprint, request, jsonify
import jwt
import datetime
import bcrypt
from database import db
from bson.objectid import ObjectId
import config  # Güncellenmiş `config.py` dosyasını içe aktarıyoruz

auth_bp = Blueprint('auth', __name__)

users_collection = db["users"]

def generate_token(user_id):
    exp_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=config.JWT_ACCESS_TOKEN_EXPIRES)
    token = jwt.encode(
        {
            "sub": str(user_id),  # Burada "sub" (subject) claim'ini ekledik
            "exp": exp_time
        },
        config.JWT_SECRET_KEY,
        algorithm="HS256"
    )
    return token, exp_time

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
        "salt": salt.decode('utf-8'),
        "token_expiry": datetime.datetime.utcnow() + datetime.timedelta(seconds=config.JWT_ACCESS_TOKEN_EXPIRES),
    }

    inserted_user = users_collection.insert_one(user_data)
    token, exp_time = generate_token(inserted_user.inserted_id)

    users_collection.update_one(
        {"_id": inserted_user.inserted_id},
        {"$set": {"token_expiry": exp_time}}
    )

    return jsonify({'message': 'Kullanıcı başarıyla kaydedildi!', 'token': token}), 201

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

    user_id = str(user["_id"])
    
    if "token_expiry" in user and datetime.datetime.utcnow() < user["token_expiry"]:
        token = jwt.encode(
            {
                "sub": user_id,  # Burada "sub" claim'ini ekledik
                "exp": user["token_expiry"]
            },
            config.JWT_SECRET_KEY,
            algorithm="HS256"
        )
    else:
        token, exp_time = generate_token(user_id)
        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"token_expiry": exp_time}})

    return jsonify({'token': token}), 200
