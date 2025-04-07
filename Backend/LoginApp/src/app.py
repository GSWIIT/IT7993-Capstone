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
#from OpenSSL import SSL

load_dotenv()
BACKEND_IP = os.getenv("BACKEND_IP")
BACKEND_DOMAIN_NAME = os.getenv("BACKEND_DOMAIN_NAME")

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[f"http://{BACKEND_IP}:5173", "http://{BACKEND_DOMAIN_NAME}", "https://{BACKEND_DOMAIN_NAME}"])

# SSL Context Setup
#context = SSL.Context(SSL.TLSv1_2_METHOD)
#context.use_privatekey_file("C:\\Users\\Administrator\\Downloads\\IT7993-Capstone-main\\IT7993-Capstone-main\\Backend\\LoginApp\\src\\cert\\key.pem")
#context.use_certificate_file("C:\\Users\\Administrator\\Downloads\\IT7993-Capstone-main\\IT7993-Capstone-main\\Backend\\LoginApp\\src\\cert\\cert.pem")


#Initialize login session settings in the Flask app.
app.config['SECRET_KEY'] = "testing"  # Change this in production
app.secret_key = "testing"
app.config['SESSION_TYPE'] = 'filesystem' # Store session on the server (alternatives: 'redis', 'memcached', 'mongodb', etc.)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True  # Helps prevent tampering
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Auto-expire sessions after 30 mins
app.config["SESSION_COOKIE_SAMESITE"] = "None" #needed for cross site cookies to work
app.config["SESSION_COOKIE_SECURE"] = True  # Required if using SameSite=None

# The maximum number of sessions the server stores in the file system
# before it starts deleting some, default 500
app.config['SESSION_FILE_THRESHOLD'] = 100

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
    serve(app, host="0.0.0.0", port=5000) #run app officially with Waitress
    #app.run(host='0.0.0.0', debug=True, port=5000)

    #ssl_context=("C:\\Users\\Administrator\\Downloads\\IT7993-Capstone-main\\IT7993-Capstone-main\\Backend\\LoginApp\\src\\cert\\cert.pem", "C:\\Users\\Administrator\\Downloads\\IT7993-Capstone-main\\IT7993-Capstone-main\\Backend\\LoginApp\\src\\cert\\key.pem"),