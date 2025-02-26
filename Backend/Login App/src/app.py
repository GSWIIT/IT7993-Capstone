from flask import Flask, render_template, request, jsonify
import logging
from settings.settings import CAMERA, FACE_DETECTION, PATHS
from login import login_bp  # Import the blueprint from login.py
from home import home_bp  # Import the blueprint from login.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This allows all origins to access your API

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Register Blueprints (added by Steven K)
app.register_blueprint(login_bp, url_prefix='/auth')  # Prefix all login routes with /auth
app.register_blueprint(home_bp, url_prefix='/home')  # Prefix all homepage routes with /home
    
if __name__ == '__main__':
    app.run(debug=True)