from flask import Flask
from flask_cors import CORS
from routers.authentication import auth_bp
from flask_jwt_extended import JWTManager
from routers.chat import chat_bp
from routers.page1 import page1_bp
from routers.page2 import page2_bp
from routers.page3 import page3_bp
from routers.page4 import page4_bp
from routers.page5 import page5_bp
import config

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8080", "https://yourfrontenddomain.com"]}})

# Flask config yükleme
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
app.config["JWT_TOKEN_LOCATION"] = config.JWT_TOKEN_LOCATION
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.JWT_ACCESS_TOKEN_EXPIRES

# JWT Manager başlat
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(page1_bp, url_prefix='/api/page1')
app.register_blueprint(page2_bp, url_prefix='/api/page2')
app.register_blueprint(page3_bp, url_prefix='/api/page3')
app.register_blueprint(page4_bp, url_prefix='/api/page4')
app.register_blueprint(page5_bp, url_prefix='/api/page5')


if __name__ == '__main__':
    app.run(debug=True, port=3000)
