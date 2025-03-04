from flask import Blueprint, session, jsonify
from flask_session import Session

session_bp = Blueprint('session', __name__, template_folder='templates')

def create_session(username):
    """Creates a session for an authenticated user."""
    session['username'] = username
    print("Session created for: " + str(username))
    return session['username']

@session_bp.route('/checksession', methods=['GET'])
def get_session():
    if "username" in session:
        return jsonify({
            "logged_in": True,
            "user_id": session["user_id"],
            "username": session["username"]
        })
    else:
        return jsonify({"logged_in": False})

def destroy_session():
    """Logs out the user and destroys session."""
    session.clear()
    return {"message": "Session destroyed"}