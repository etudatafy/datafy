from flask import Blueprint, request, jsonify
from database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
import datetime

exam_bp = Blueprint('exam', __name__)
users_collection = db["users"]

DEFAULT_RESULTS = {
    "TYT": {
        "turkce": 0,
        "sosyal": 0,
        "matematik": 0,
        "fen": 0
    },
    "AYT": {
        "matematik_ayt": 0,
        "fizik": 0,
        "kimya": 0,
        "biyoloji": 0,
        "edebiyat": 0,
        "tarih_1": 0,
        "cografya_1": 0,
        "tarih_2": 0,
        "cografya_2": 0,
        "felsefe": 0,
        "din": 0
    }
}

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

def add_exam_to_user(user_id, exam_data):
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user or not is_token_valid(user):
        return None

    if "exams" not in user:
        user["exams"] = []

    new_exam = {
        "_id": ObjectId(),
        "name": exam_data["name"],
        "date": exam_data["date"],
        "results": exam_data.get("results", DEFAULT_RESULTS.copy())  # Eğer results yoksa default değer koy
    }

    user["exams"].append(new_exam)

    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"exams": user["exams"]}}
    )

    return new_exam

@exam_bp.route('/fetch-exams', methods=['GET'])
@jwt_required()
def fetch_exams():
    user_id = get_jwt_identity()
    user = get_authenticated_user(user_id)
    if not isinstance(user, dict):
        return user

    exams = user.get("exams", [])

    return jsonify([
        {
            "id": str(exam["_id"]),
            "name": exam["name"],
            "date": exam["date"],
            "results": exam.get("results", {})  # Doğrudan MongoDB'den çek
        } 
        for exam in exams
    ]), 200

@exam_bp.route('/add', methods=['POST'])
@jwt_required()
def add_exam():
    user_id = get_jwt_identity()
    user = get_authenticated_user(user_id)
    if not isinstance(user, dict):
        return user

    data = request.json

    if not data.get("name") or not data.get("date"):
        return jsonify({"error": "Eksik veri!"}), 400

    new_exam = add_exam_to_user(user_id, data)

    if not new_exam:
        return jsonify({"error": "Sınav eklenirken hata oluştu"}), 500

    return jsonify({"message": "Sınav eklendi!", "examId": str(new_exam["_id"])}), 201

@exam_bp.route('/exam-details', methods=['POST'])
@jwt_required()
def get_exam():
    user_id = get_jwt_identity()
    user = get_authenticated_user(user_id)
    if not isinstance(user, dict):
        return user

    data = request.json
    exam_id = data.get("exam_id")

    if not exam_id:
        return jsonify({"error": "exam_id eksik!"}), 400

    exam = next((exam for exam in user.get("exams", []) if str(exam["_id"]) == exam_id), None)

    if not exam:
        return jsonify({"error": "Sınav bulunamadı!"}), 404

    return jsonify({
        "id": str(exam["_id"]),
        "name": exam["name"],
        "date": exam["date"],
        "results": exam.get("results", DEFAULT_RESULTS.copy())  # Varsayılan yerine MongoDB'den çek
    }), 200

@exam_bp.route('/edit-exam', methods=['POST'])
@jwt_required()
def edit_exam():
    user_id = get_jwt_identity()
    user = get_authenticated_user(user_id)
    if not isinstance(user, dict):
        return user

    data = request.json
    exam_id = data.get("exam_id")

    if not exam_id:
        return jsonify({"error": "exam_id eksik!"}), 400

    # Kullanıcının sahip olduğu sınavı bul
    exam_filter = {"_id": ObjectId(user_id), "exams._id": ObjectId(exam_id)}

    # Güncellenmesi gereken alanlar
    update_fields = {}

    if "examName" in data:
        update_fields["exams.$.name"] = data["examName"]
    if "examDate" in data:
        update_fields["exams.$.date"] = data["examDate"]
    if "exams" in data:
        formatted_results = {exam["title"]: {subject["name"]: subject["score"] for subject in exam["subjects"]} for exam in data["exams"]}
        update_fields["exams.$.results"] = formatted_results  # Doğru şekilde results'ı güncelle

    if not update_fields:
        return jsonify({"error": "Güncellenecek veri yok!"}), 400

    # Güncelleme işlemi
    result = users_collection.update_one(
        exam_filter,
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Sınav bulunamadı veya güncellenemedi!"}), 404

    return jsonify({"message": "Sınav başarıyla güncellendi!"}), 200

@exam_bp.route('/delete-exam', methods=['POST'])
@jwt_required()
def delete_exam():
    user_id = get_jwt_identity()
    user = get_authenticated_user(user_id)
    if not isinstance(user, dict):
        return user

    data = request.json
    exam_id = data.get("exam_id")

    if not exam_id:
        return jsonify({"error": "exam_id eksik!"}), 400

    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"exams": {"_id": ObjectId(exam_id)}}}
    )

    if result.modified_count == 0:
        return jsonify({"error": "Sınav bulunamadı veya silinemedi!"}), 404

    return jsonify({"message": "Sınav başarıyla silindi!"}), 200
