from flask import Flask
from flask_cors import CORS
from routers.authentication import auth_bp
from routers.page1 import page1_bp
from routers.page2 import page2_bp
from routers.page3 import page3_bp
from routers.page4 import page4_bp
from routers.page5 import page5_bp

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5174", "https://yourfrontenddomain.com"]}})

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(page1_bp, url_prefix='/api/page1')
app.register_blueprint(page2_bp, url_prefix='/api/page2')
app.register_blueprint(page3_bp, url_prefix='/api/page3')
app.register_blueprint(page4_bp, url_prefix='/api/page4')
app.register_blueprint(page5_bp, url_prefix='/api/page5')

if __name__ == '__main__':
    app.run(debug=True, port=3000)
