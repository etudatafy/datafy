from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
import datetime
from database import db
import config  

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

users_collection = db["users"]

@socketio.on("connect")
@jwt_required()
def handle_connect():
    user_id = get_jwt_identity()
    print(f"Kullanıcı {user_id} bağlandı.")

@socketio.on("join_room")
@jwt_required()
def handle_join_room(data):
    user_id = get_jwt_identity()
    other_user_id = data.get("otherUserId")

    if not other_user_id:
        return

    room = f"chat_{min(user_id, other_user_id)}_{max(user_id, other_user_id)}"
    join_room(room)
    print(f"{user_id} {room} odasına katıldı.")

@socketio.on("send_message")
@jwt_required()
def handle_send_message(data):
    user_id = get_jwt_identity()
    other_user_id = data.get("otherUserId")
    message_text = data.get("message", "").strip()

    if not message_text or not other_user_id:
        return

    room = f"chat_{min(user_id, other_user_id)}_{max(user_id, other_user_id)}"
    timestamp = datetime.datetime.utcnow()

    message_data = {
        "sender": user_id,
        "receiver": other_user_id,
        "text": message_text,
        "timestamp": timestamp
    }

    # Veritabanına mesajı kaydet
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"chat_histories": {"other_user_id": other_user_id, "message": message_data}}}
    )
    
    users_collection.update_one(
        {"_id": ObjectId(other_user_id)},
        {"$push": {"chat_histories": {"other_user_id": user_id, "message": message_data}}}
    )

    emit("receive_message", message_data, room=room)

@socketio.on("disconnect")
@jwt_required()
def handle_disconnect():
    user_id = get_jwt_identity()
    print(f"Kullanıcı {user_id} bağlantıyı kapattı.")

if __name__ == "__main__":
    socketio.run(app, debug=True)
