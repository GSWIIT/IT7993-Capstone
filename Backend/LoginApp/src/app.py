import os
from flask import Flask
from flask_session import Session
import logging
from login import login_bp  # Import the blueprint from login.py
from permissions import permissions_bp
from account import account_bp
from flask_cors import CORS
from datetime import timedelta
from dotenv import load_dotenv
from waitress import serve
import secrets

def string_to_bool(string):
    string = string.lower()
    if string in ('true', '1', 'yes'):
        return True
    elif string in ('false', '0', 'no'):
        return False
    else:
        raise ValueError('Invalid boolean string')

load_dotenv()
BACKEND_DOMAIN_NAME = os.getenv("BACKEND_DOMAIN_NAME")
RUN_FLASK_LOCALLY = os.getenv("RUN_FLASK_LOCALLY")

# Generate a random secret key with 32 bytes (256 bits), used to secure login sessions
secret_key = secrets.token_urlsafe(32)

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[f"http://{BACKEND_DOMAIN_NAME}", f"https://{BACKEND_DOMAIN_NAME}", "http://localhost:5173", "http://localhost"])

#Initialize login session settings in the Flask app.
app.config['SECRET_KEY'] = secret_key  # Change this in production
app.secret_key = secret_key
app.config['SESSION_TYPE'] = 'filesystem' # Store session on the server (alternatives: 'redis', 'memcached', 'mongodb', etc.)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True  # Helps prevent tampering
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_PERMANENT'] = True #allow sessions to refresh themselves on request
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Auto-expire sessions after 30 mins of session inactivity
app.config["SESSION_COOKIE_SAMESITE"] = "None" #needed for cross site cookies to work
app.config["SESSION_COOKIE_SECURE"] = True  # Required if using SameSite=None

# The maximum number of sessions the server stores in the file system before it starts deleting some, default 500
app.config['SESSION_FILE_THRESHOLD'] = 500

#start Flask login session handler
Session(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Register Blueprints
app.register_blueprint(login_bp, url_prefix='/auth')  # Prefix all login routes with /auth
app.register_blueprint(permissions_bp, url_prefix='/permissions')  # Prefix all permission routes with /permissions
app.register_blueprint(account_bp, url_prefix='/account')
    
if __name__ == '__main__':
    if(string_to_bool(RUN_FLASK_LOCALLY)):
        app.run(debug=True, port=5000) #run locally in dev mode
    else:
        serve(app, host="0.0.0.0", port=5000) #run app officially on network with Waitress