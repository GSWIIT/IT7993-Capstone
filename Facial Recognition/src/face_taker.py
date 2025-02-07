# Suppress macOS warning
import warnings
warnings.filterwarnings('ignore', category=UserWarning)
import sys
import json
import cv2
import os
from typing import Optional, Dict
import logging
from settings.settings import CAMERA, FACE_DETECTION, TRAINING, PATHS
import subprocess
import numpy as np
import face_recognition


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_directory(directory: str) -> None:
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
    except OSError as e:
        logger.error(f"Error creating directory {directory}: {e}")
        raise

def get_face_id(directory: str) -> int:
    """
    Get the first available face ID by checking existing files.
    
    Parameters:
        directory (str): The path of the directory of images.
    Returns:
        int: The next available face ID
    """
    try:
        if not os.path.exists(directory):
            return 1
            
        user_ids = []
        for filename in os.listdir(directory):
            if filename.startswith('Users-'):
                try:
                    number = int(filename.split('-')[1])
                    user_ids.append(number)
                except (IndexError, ValueError):
                    continue
                    
        return max(user_ids + [0]) + 1
    except Exception as e:
        logger.error(f"Error getting face ID: {e}")
        raise

def save_name(face_id: int, face_name: str, filename: str) -> None:
    """
    Save name-ID mapping to JSON file
    
    Parameters:
        face_id (int): The identifier of user
        face_name (str): The user name
        filename (str): Path to the JSON file
    """
    try:
        names_json: Dict[str, str] = {}
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as fs:
                    content = fs.read().strip()
                    if content:  # Only try to load if file is not empty
                        names_json = json.loads(content)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in {filename}, starting fresh")
                names_json = {}
        
        names_json[str(face_id)] = face_name
        
        with open(filename, 'w') as fs:
            json.dump(names_json, fs, indent=4, ensure_ascii=False)
        logger.info(f"Saved name mapping for ID {face_id}")
    except Exception as e:
        logger.error(f"Error saving name mapping: {e}")
        raise

def initialize_camera(camera_index: int = 0) -> Optional[cv2.VideoCapture]:
    """
    Initialize the camera with error handling
    
    Parameters:
        camera_index (int): Camera device index
    Returns:
        cv2.VideoCapture or None: Initialized camera object
    """
    try:
        cam = cv2.VideoCapture(camera_index)
        if not cam.isOpened():
            logger.error("Could not open webcam")
            return None
            
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA['width'])
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA['height'])
        return cam
    except Exception as e:
        logger.error(f"Error initializing camera: {e}")
        return None

def is_duplicate_face(new_face_img, image_dir: str, threshold: float = 0.6) -> bool:
    """
    Compare the new face with existing stored faces using Dlib face recognition.

    Parameters:
        new_face_img (numpy.ndarray): Grayscale image of the new face.
        image_dir (str): Directory containing stored face images.
        threshold (float): Face similarity threshold (lower = stricter match).
    
    Returns:
        bool: True if a duplicate face is found, otherwise False.
    """
    logger = logging.getLogger(__name__)

    # Convert grayscale to RGB (Dlib needs RGB images)
    new_face_img = cv2.cvtColor(new_face_img, cv2.COLOR_GRAY2RGB)

    # Encode the new face
    new_face_encoding = face_recognition.face_encodings(new_face_img)
    if len(new_face_encoding) == 0:
        logger.error("No face encoding found in the new image.")
        return False  # No face detected

    new_face_encoding = new_face_encoding[0]  # Take the first detected face

    for filename in os.listdir(image_dir):
        if filename.endswith('.jpg') and filename.startswith('Users-'):
            img_path = os.path.join(image_dir, filename)
            stored_img = face_recognition.load_image_file(img_path)

            # Encode stored face
            stored_face_encoding = face_recognition.face_encodings(stored_img)
            if len(stored_face_encoding) == 0:
                continue  # Skip if no encoding found

            stored_face_encoding = stored_face_encoding[0]

            # Compare faces
            face_distance = face_recognition.face_distance([stored_face_encoding], new_face_encoding)[0]
            logger.info(f"Comparing with {filename}: Similarity Score = {1 - face_distance}")

            if face_distance < threshold:  # Lower distance = more similar
                logger.info(f"Match found with {filename}. This face is already registered.")
                return True

    return False  # No duplicate found


if __name__ == '__main__':
    try:
        # Initialize
        create_directory(PATHS['image_dir'])
        face_cascade = cv2.CascadeClassifier(PATHS['cascade_file'])
        if face_cascade.empty():
            raise ValueError("Error loading cascade classifier")
            
        cam = initialize_camera(CAMERA['index'])
        if cam is None:
            raise ValueError("Failed to initialize camera")
            
        # Get user info
        print("Debug: Script started")  # Debugging print

        if len(sys.argv) > 1:
            face_name = " ".join(sys.argv[1:]).strip()
            print(f"Debug: Received username -> {face_name}")  # Debugging print
        else:
            print("Error: No name provided.")
            exit(1)
        if not face_name:
            raise ValueError("Name cannot be empty")

        # Capture a sample image to check for duplicates
        # Capture a sample image to check for duplicates
        ret, img = cam.read()
        if not ret:
            raise ValueError("Failed to capture image for verification")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=FACE_DETECTION['scale_factor'], 
                                              minNeighbors=FACE_DETECTION['min_neighbors'], 
                                              minSize=FACE_DETECTION['min_size'])

        if len(faces) == 0:
            raise ValueError("No face detected. Please try again.")

        x, y, w, h = faces[0]  # Take the first detected face
        face_img = gray[y:y+h, x:x+w]

        # Check if the face is a duplicate
        if is_duplicate_face(face_img, PATHS['image_dir'], threshold=0.6):
            logger.error("This face is already registered. Duplicate entries are not allowed.")
            cam.release()
            cv2.destroyAllWindows()
            sys.exit(1)


        # Assign a new ID and save
        face_id = get_face_id(PATHS['image_dir'])
        save_name(face_id, face_name, PATHS['names_file'])

        
        logger.info(f"Initializing face capture for {face_name} (ID: {face_id})")
        logger.info("Look at the camera and wait...")
        
        count = 0
        while True:
            ret, img = cam.read()
            if not ret:
                logger.warning("Failed to grab frame")
                continue
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=FACE_DETECTION['scale_factor'],
                minNeighbors=FACE_DETECTION['min_neighbors'],
                minSize=FACE_DETECTION['min_size']
            )
            
            for (x, y, w, h) in faces:
                if count < TRAINING['samples_needed']:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    
                    face_img = gray[y:y+h, x:x+w]
                    img_path = f'./{PATHS["image_dir"]}/Users-{face_id}-{count+1}.jpg'
                    cv2.imwrite(img_path, face_img)
                    
                    try:
                        subprocess.run(["python3", ".\src\hash_generator.py"], check=True)
                    except Exception as e:
                        logger.error(f"Error generating hash: {e}")
                    count += 1
                    
                    progress = f"Capturing: {count}/{TRAINING['samples_needed']}"
                    cv2.putText(img, progress, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    break
            
            cv2.imshow('Face Capture', img)
            
            if cv2.waitKey(100) & 0xff == 27:  # ESC key
                break
            if count >= TRAINING['samples_needed']:
                break
                
        logger.info(f"Successfully captured {count} images")
        print(f"Debug: Received username -> {face_name}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        
    finally:
        if 'cam' in locals():
            cam.release()
        cv2.destroyAllWindows()
print("Face capture completed successfully.")
sys.exit(0)  # Exit with success