from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
import datetime
from database import db

users_collection = db["users"]

def is_token_valid(user):
    if "token_expiry" not in user or datetime.datetime.utcnow() > user["token_expiry"]:
        return False
    return True

def get_authenticated_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"error": "Kullanıcı bulunamadı"}), 404

    if not is_token_valid(user):
        return jsonify({"error": "Token geçersiz veya süresi dolmuş"}), 401

    return user

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/exam-details', methods=['GET'])
@jwt_required()
def progress_exam_details():
    user_id = get_jwt_identity()
    user = get_authenticated_user(user_id)
    if not user or not is_token_valid(user):
        return jsonify({"error": "Kullanıcı doğrulanamadı veya token geçersiz."}), 401

    if "exams" not in user:
        user["exams"] = []

    exams = user.get("exams", [])
    return jsonify([
        {
            "id": str(exam["_id"]),
            "name": exam["name"],
            "date": exam["date"],
            "results": exam.get("results", {})
        }
        for exam in exams
    ]), 200