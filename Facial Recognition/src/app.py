from flask import Flask, render_template, request, jsonify
import subprocess
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Render the HTML UI."""
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    """Handle user registration via Flask form."""
    face_name = request.form.get('face_name')
    
    if not face_name:
        return jsonify({"error": "Name cannot be empty"})

    try:
        logger.info(f"Starting face capture for {face_name}")

        # Run face_taker.py in background (no blocking)
        subprocess.Popen(["python3", "./src/face_taker.py", face_name], shell=False)

        logger.info(f"Face capture process started for {face_name}")
        return jsonify({"success": f"Face capture started for {face_name}"})

    except Exception as e:
        logger.error(f"Failed to register face: {str(e)}")
        return jsonify({"error": f"Failed to register face: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
