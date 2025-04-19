from flask import Blueprint, request, jsonify
from database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
import datetime
import requests
import config
import os
from dotenv import load_dotenv
from pathlib import Path
import json

chat_bp = Blueprint('chat', __name__)
users_collection = db["users"]

env = os.getenv("FLASK_ENV", "production")

if env == "development":
    base_dir = Path(__file__).resolve().parent
    load_dotenv(dotenv_path=base_dir / ".env.development", override=True)

chat_root_url = os.getenv("CHAT_ROOT", "").split(",")
chat_root_url = chat_root_url[0]

print(f"[{env}] Using CHAT URL: {chat_root_url}")

def is_token_valid(user):
    if "token_expiry" not in user or datetime.datetime.utcnow() > user["token_expiry"]:
        return False
    return True

def add_message_to_chat(user_id, chat_id, text, sender_type):
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user or "ai-chat-histories" not in user:
        return None

    chat = next((chat for chat in user["ai-chat-histories"] if str(chat["_id"]) == chat_id), None)
    if not chat:
        return None

    chat["messages"].append({"text": text, "sender": sender_type})

    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"ai-chat-histories": user["ai-chat-histories"]}}
    )

    return chat["messages"]

@chat_bp.route('/update-chat', methods=['POST'])
@jwt_required()
def chat():
    global chat_root_url
    user_id = get_jwt_identity()
    data = request.json
    chat_type = data.get("type")
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Boş mesaj gönderilemez"}), 400

    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"error": "Kullanıcı bulunamadı"}), 404

    if not is_token_valid(user):
        return jsonify({"error": "Token geçersiz veya süresi dolmuş"}), 401

    if "ai-chat-histories" not in user:
        user["ai-chat-histories"] = []

    if chat_type == 1:
        if config.chat_test_mode == True:
            model_response = "Hello World"
        else:
            # FastAPI backend'e istek gönder
            exams = user.get("exams", [])
            full_query = (
                "Sınav bilgileri:\n" +
                json.dumps(exams, ensure_ascii=False, indent=2) +
                "\n\nKullanıcı mesajı:\n" +
                user_message
            )
            full_query = f"Sınavlar:\n{full_query}\n\nKullanıcı: {user_message}"
            payload = {"query": full_query, "user_id": str(user_id)}
            try:
                resp = requests.post(chat_root_url + "/query", json=payload)
                resp.raise_for_status()
                model_response = resp.json().get("response", "")
            except Exception as e:
                model_response = f"Hata: {e}"

        new_chat = {
            "_id": ObjectId(),
            "messages": [
                {"text": user_message, "sender": "sender"},
                {"text": model_response, "sender": "receiver"}
            ]
        }

        inserted_chat = db["ai-chat-histories"].insert_one(new_chat)

        user["ai-chat-histories"].append({
            "_id": inserted_chat.inserted_id,
            "messages": new_chat["messages"]
        })

        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"ai-chat-histories": user["ai-chat-histories"]}}
        )

        return jsonify({"chatId": str(inserted_chat.inserted_id)})

    elif chat_type == 2:
        chat_id = data.get("chatId")
        if not chat_id:
            return jsonify({"error": "chatId eksik"}), 400

        messages = add_message_to_chat(user_id, chat_id, user_message, "sender")
        if messages is None:
            return jsonify({"error": "Sohbet bulunamadı"}), 404

        if getattr(config, 'chat_test_mode', False):
            model_response = "Hello World"
        else:
            exams = user.get("exams", [])
            full_query = (
                "Sınav bilgileri:\n" +
                json.dumps(exams, ensure_ascii=False, indent=2) +
                "\n\nKullanıcı mesajı:\n" +
                user_message
            )
            full_query = f"Sınavlar:\n{full_query}\n\nKullanıcı: {user_message}"
            payload = {"query": full_query, "user_id": str(user_id)}
            try:
                resp = requests.post(chat_root_url + "/query", json=payload)
                resp.raise_for_status()
                model_response = resp.json().get("response", "")
            except Exception as e:
                model_response = f"Hata: {e}"

        messages = add_message_to_chat(user_id, chat_id, model_response, "receiver")

        return jsonify({"messages": messages})

    return jsonify({"error": "Geçersiz istek"}), 400

@chat_bp.route('/chat-history', methods=['POST'])
@jwt_required()
def chat_history():
    user_id = get_jwt_identity()
    data = request.json
    chat_id = data.get("chatId")

    if not chat_id:
        return jsonify({"error": "chatId eksik"}), 400

    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"error": "Kullanıcı bulunamadı"}), 404

    if not is_token_valid(user):
        return jsonify({"error": "Token geçersiz veya süresi dolmuş"}), 401

    chat = next((chat for chat in user["ai-chat-histories"] if str(chat["_id"]) == chat_id), None)

    if not chat:
        return jsonify({"error": "Sohbet bulunamadı"}), 404

    return jsonify({"messages": chat["messages"]})
