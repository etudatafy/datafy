import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from routers.authentication import auth_bp
from routers.chat           import chat_bp
from routers.exam           import exam_bp
from routers.progress       import progress_bp
import config

if os.getenv("FLASK_ENV") == "development":
    base_dir = Path(__file__).resolve().parent
    load_dotenv(dotenv_path=base_dir / ".env.development")

app = Flask(__name__)

frontend_origins = os.getenv("FRONTEND_ROOT", "").split(",")
CORS(app, resources={r"/api/*": {"origins": frontend_origins}})

app.config["JWT_SECRET_KEY"]           = config.JWT_SECRET_KEY
app.config["JWT_TOKEN_LOCATION"]       = config.JWT_TOKEN_LOCATION
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.JWT_ACCESS_TOKEN_EXPIRES

jwt = JWTManager(app)

app.register_blueprint(auth_bp,      url_prefix='/api/auth')
app.register_blueprint(chat_bp,      url_prefix='/api/chat')
app.register_blueprint(exam_bp,      url_prefix='/api/exam')
app.register_blueprint(progress_bp,  url_prefix='/api/progress')

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_ENV") == "development"
    app.run(debug=debug_mode, port=3000)