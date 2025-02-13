from flask import Flask, render_template, request, jsonify
import subprocess
import logging
import cv2
import os
import json
from settings.settings import CAMERA, FACE_DETECTION, PATHS
from face_recognizer import initialize_camera, load_names
from login import login_bp  # Import the blueprint from login.py
from home import home_bp  # Import the blueprint from login.py

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Register Blueprints (added by Steven K)
app.register_blueprint(login_bp, url_prefix='/auth')  # Prefix all login routes with /auth
app.register_blueprint(home_bp, url_prefix='/home')  # Prefix all homepage routes with /home

# Load face recognizer and cascade classifier
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(PATHS['trainer_file'])
face_cascade = cv2.CascadeClassifier(PATHS['cascade_file'])
names = load_names(PATHS['names_file'])

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
        result = subprocess.Popen(["python", "./src/face_taker.py", face_name], shell=False)
        result.wait()
        if result.returncode == 0:
            subprocess.Popen(["python", "./src/face_trainer.py", face_name], shell=False)
            return jsonify({"success": f"Face capture completed for {face_name}"})
        elif result.returncode == 1:
            return jsonify({"error": "This face is already registered. Duplicate entries are not allowed."})
        else:
            return jsonify({"error": f"Face capture failed with code {result.returncode}."}) 
        #logger.info(f"Face capture process started for {face_name}")
        #return jsonify({"success": f"Face capture started for {face_name}"})
        
    except Exception as e:
        logger.error(f"Failed to register face: {str(e)}")
        return jsonify({"error": f"Failed to register face: {str(e)}"})
    
@app.route('/scan', methods=['POST'])
def scan_face():
    input_name = request.form.get('face_name')
    if not input_name:
        return jsonify({"error": "No name provided"}), 400

    try:
        cam = initialize_camera(CAMERA['index'])
        if cam is None:
            raise ValueError("Failed to initialize camera")

        import time
        start_time = time.time()
        match_found = False

        while time.time() - start_time < 10:  # Run for 10 seconds
            ret, img = cam.read()
            if not ret:
                raise ValueError("Failed to grab frame")

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=FACE_DETECTION['scale_factor'],
                minNeighbors=FACE_DETECTION['min_neighbors'],
                minSize=FACE_DETECTION['min_size']
            )

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
                recognized_name = names.get(str(id), "Unknown")
                result = "MATCH"
                if confidence <= 100:
                    name = names.get(str(id), "Unknown")
                    confidence_text = f"{confidence:.1f}%"
                    
                    # Display name and confidence
                    cv2.putText(img, name, (x+5, y-5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(img, confidence_text, (x+5, y+h-5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 1)
                cv2.imshow('Face Recognition', img)    
               
                if recognized_name == input_name:
                    match_found = True
                    break

            cv2.imshow('Face Recognition', img)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit early
                break

        cv2.destroyAllWindows()

        if match_found:
            return jsonify({"success": f"MATCH - {input_name}"}), 200
        else:
            return jsonify({"error": f"No match found for - {input_name}"}), 200

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if 'cam' in locals():
            cam.release()
    
def print():
    output = "Sucessfully registered!"
    return render_template('index.html', message=output)    
    
if __name__ == '__main__':
    app.run(debug=True)