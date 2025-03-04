from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import logging
from settings.settings import CAMERA, FACE_DETECTION, PATHS
from login import login_bp  # Import the blueprint from login.py
from home import home_bp  # Import the blueprint from login.py
from session import session_bp
from flask_cors import CORS
import os
from datetime import timedelta

# Session configuration (to be included in your Flask app)
SESSION_TYPE = 'filesystem'  # Store session on the server (alternatives: 'redis', 'memcached', 'mongodb', etc.)
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True  # Helps prevent tampering
SESSION_COOKIE_HTTPONLY = True  # Prevents JavaScript from accessing session cookie
SESSION_COOKIE_SECURE = False  # Set to True if using HTTPS
PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # Auto-expire session after 30 minutes

app = Flask(__name__)
CORS(app)  # This allows all origins to access your API

"""Initialize session settings in the Flask app."""
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')  # Change this in production
app.config['SESSION_TYPE'] = SESSION_TYPE
app.config['SESSION_PERMANENT'] = SESSION_PERMANENT
app.config['SESSION_USE_SIGNER'] = SESSION_USE_SIGNER
app.config['SESSION_COOKIE_HTTPONLY'] = SESSION_COOKIE_HTTPONLY
app.config['SESSION_COOKIE_SECURE'] = SESSION_COOKIE_SECURE
app.config['PERMANENT_SESSION_LIFETIME'] = PERMANENT_SESSION_LIFETIME

#start Flask session handler
Session(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Register Blueprints (added by Steven K)
app.register_blueprint(login_bp, url_prefix='/auth')  # Prefix all login routes with /auth
app.register_blueprint(home_bp, url_prefix='/home')  # Prefix all homepage routes with /home
app.register_blueprint(session_bp, url_prefix='/session')  # Prefix all homepage routes with /home
    
if __name__ == '__main__':
    app.run(debug=True)

