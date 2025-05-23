from flask import Blueprint, render_template, request, session, jsonify
import hashlib
import time
import cv2
import numpy as np
import base64
from PIL import Image
import imagehash
from imagehash import dhash
import io
import face_recognition
from functools import wraps
from datetime import datetime
from blockchain_connection import get_contract, get_w3_object, write_to_blockchain

login_bp = Blueprint('login', __name__, template_folder='templates')

# Load OpenCV's pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

contract = get_contract()
w3 = get_w3_object()

#a list to hold users temporarily while they are trying to 2FA, so we don't have to query the blockchain every time.
temporary_user_storage = []

#NUM_PERM = 128  # Ensure the same number of permutations throughout

def hash_password(password: str) -> str:
    """Simulates hashing of password (should match how it's stored in contract)."""
    return hashlib.sha256(password.encode()).hexdigest()

#this function checks the smart contract to see if a username already exists
def check_username_exists(username):
    user_obj = contract.functions.checkIfUserExists(username).call()
    print(user_obj)
    if user_obj == False:
        print("Username does not exist in system yet.")
        return False
    else:
        print("Username exists in system already!")
        return True
    
def hash_face_encoding(face_encoding):
    """ Convert the face encoding to a Locality-Sensitive Hash (LSH) """
    # Normalize and convert encoding to a string
    encoding_str = ''.join(format(int(e * 1000), '04x') for e in face_encoding)

    # Use a perceptual hash (dhash) for stability
    hash_value = dhash(Image.fromarray(np.uint8(face_encoding.reshape(16, 8) * 255)))
    
    return str(hash_value)

def hamming_distance(hash1, hash2):
    """ Calculate the Hamming Distance between two hex hashes """
    # Convert hex hashes to binary
    bin1 = bin(int(hash1, 16))[2:].zfill(64)  # Ensures 64-bit length
    bin2 = bin(int(hash2, 16))[2:].zfill(64)

    # Count differing bits
    return sum(c1 != c2 for c1, c2 in zip(bin1, bin2))

def send_login_success_log(username):
    try:
        print("Sending login success log...")
        write_to_blockchain(contract.functions.emitLoginSuccessLog, [username])
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: "  + str(e.args[0]) + "!"})
    
def generate_face_hash(face_img):
    """Generate a hash from the detected face for authentication purposes."""
    face_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    _, face_encoded = cv2.imencode('.png', face_gray)  # Encode face as PNG
    face_bytes = face_encoded.tobytes()  # Convert to bytes
    return hashlib.sha256(face_bytes).hexdigest()[:8]  # Generate SHA-256 hash

def perceptual_hash_from_base64(base64_string):
    image = base64_to_image(base64_string)
    #image = image.convert("L")
    return imagehash.phash(image)

def base64_to_image(base64_string):
    # Decode the base64 string into binary data
    image_data = base64.b64decode(base64_string)

    # Convert binary data to a BytesIO stream
    image_stream = io.BytesIO(image_data)

    # Open the image using PIL
    image = Image.open(image_stream)

    return image

def scan_image_for_face(img):
    #img is byte64 string, represents image
    # Decode Base64 back to an image
    img_data = base64.b64decode(img)
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Convert to grayscale for better face detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) < 1:
        return {"success": False, "reason": "No face detected in image."}
    if len(faces) > 1:
        return {"success": False, "reason": "Too many faces detected in image."}

    print(f"Detected {len(faces)} face(s).")

    for (x, y, w, h) in faces:
        img_copy = img.copy()

        #draw rectangle on image
        cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)

        _, buffer = cv2.imencode('.png', img_copy)
        face_preview_base64_img = base64.b64encode(buffer).decode('utf-8')

        return {"success": True, "reason": "OpenCV ran successfully on provided image.", "image": face_preview_base64_img}
    
def create_lsh_from_image(img):
    #img is byte64 string, represents image
    # Decode Base64 back to an image
    img_data = base64.b64decode(img)
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Convert to grayscale for better face detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) < 1:
        return {"success": False, "reason": "No face detected in image."}
    if len(faces) > 1:
        return {"success": False, "reason": "Too many faces detected in image."}

    print(f"Detected {len(faces)} face(s).")

    for (x, y, w, h) in faces:
        img_copy = img.copy()

        #draw rectangle on image with OpenCV
        cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)

        _, buffer = cv2.imencode('.png', img_copy)
        face_preview_base64_img = base64.b64encode(buffer).decode('utf-8')

    # Get face encodings from the image
    encodings = face_recognition.face_encodings(img)
    if encodings:
        face_encoding = encodings[0] #there should only be one face, so we can always take the first item in the array.
        print("Face encoding obtained.")
    else:
        print("No face encoding found.")
        return {"success": False, "reason": "No face encoding found.", "preview": None}

    lsh_hash_obj = hash_face_encoding(face_encoding)
        
    return {"success": True, "reason": "OpenCV ran successfully. Face encoding created and hashed successfully.", "hash": lsh_hash_obj, "preview": face_preview_base64_img}

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        
        password = hash_password(password)

        user_obj = contract.functions.getUser(username).call()
        print(user_obj)
        if user_obj[0] == "":
            print("The username and/or password is incorrect.")
            return jsonify({"success": False, "reason": "The username and/or password is incorrect."})
        else:
            #now we compare the password hashes to see if they match
            if password == user_obj[1]:
                print("Username and password match! First portion of login was successful!")
                return jsonify({"success": True, "reason": "Username and password match! Login was successful!"})
            else:
                print("The password entered is incorrect.")
                return jsonify({"success": False, "reason": "The username and/or password is incorrect."})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})

@login_bp.route('/login-2FA-Face', methods=['POST'])
def check_face_for_2FA():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        frames = data.get("frames")
        
        password = hash_password(password)
        user_obj = None

        for tempUser in temporary_user_storage:
            if tempUser[0] == username:
                print(tempUser)
                print("Pulled user from temp array.")
                user_obj = tempUser
                break

        if user_obj is None:
            user_obj = contract.functions.getUser(username).call()
            print(user_obj)
            if user_obj[0] == "":
                print("The username and/or password is incorrect.")
                return jsonify({"success": False, "reason": "The username and/or password is incorrect."})
            else:
                #now we compare the password hashes to see if they match
                if password == user_obj[1]:
                    print("Username and password match! First portion of login was successful!")
                    temporary_user_storage.append(user_obj)
                else:
                    print("The password entered is incorrect.")
                    return jsonify({"success": False, "reason": "The username and/or password is incorrect."})

        #finally, compare euclidean distance of three detected faces for similarity comparison.
        hamming_distance_limit = 8
        frame_face_images = []

        for frameIndex, frameToScan in enumerate(frames):
            #need to make sure frame is not empty before trying to scan it
            if(frameToScan is None) or (frameToScan == ""):
                continue

            frameEncoding = create_lsh_from_image(frameToScan)
            
            if frameEncoding["success"]:
                frame_face_images.append(frameEncoding["preview"])
                print("Comparing face embeddings with frame " + str(frameIndex) + "...")
                for hashIndex, userHash in enumerate(user_obj[2]):
                    # Compute Euclidean distance
                    print(frameEncoding["hash"])
                    print(userHash)
                    results = hamming_distance(frameEncoding["hash"], userHash)
                    print("Hamming distance [Frame " + str(frameIndex) + " vs User LSH " + str(hashIndex) + "]: " + str(results))
                    if results <= hamming_distance_limit:
                        print("Hamming distance below limit. Returning success...")
                        temporary_user_storage.pop()
                        session.clear()
                        session["username"] = username

                        send_login_success_log(username)

                        return jsonify({"success": True, "reason": "Face verified successfully. Login successful!", "preview": frame_face_images})
        
        #temporary_user_storage.pop()
        return jsonify({"success": False, "reason": "User's face not detected.", "preview": frame_face_images})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})

@login_bp.route('/usernamecheck', methods=['POST'])
def check_sent_username():
    try:
        data = request.get_json()
        username = data.get("username")
        
        result = check_username_exists(username)
        time.sleep(1)
        if result == True:
            return jsonify({"success": False, "reason": "ERROR: Username already exists on the smart contract! Please create a unique username to continue."})
        else:
            return jsonify({"success": True, "reason": "Username is available."})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})

@login_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        faceImages = data.get("faceArray")

        #hash password
        password = hash_password(password)

        result = check_username_exists(username)
        time.sleep(1)
        if result == True:
            return jsonify({"success": False, "reason": "ERROR: Username already exists on the smart contract! Please create a unique username to continue."})

        if len(faceImages) != 3:
            return jsonify({"success": False, "reason": "ERROR: You must send three images to the server to continue."})
        
        #get face hash data from images
        face_image_data = []
        for img in faceImages:
            #result = scan_image_for_face(img)
            result = create_lsh_from_image(img)
            if result["success"]:
                face_image_data.append(result)
            else:
                return jsonify ({"success": False, "reason": result["reason"]})
            
        print("Face hashes obtained.")

        face_hash_array = []
        for face in face_image_data:
            face_hash_array.append(face["hash"])

        #get the current date in YYYY_MM_DD format, used for creation date of account
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_date = str(current_date)

        transaction = write_to_blockchain(contract.functions.registerUser, [username, password, face_hash_array, current_date])

        # Wait for confirmation of transaction
        receipt = w3.eth.wait_for_transaction_receipt(transaction)

        # Print transaction status
        if receipt.status == 1:
            print(f"Transaction successful! Block: {receipt.blockNumber}")
            print("Waiting a few more seconds...")
            time.sleep(5)
            return jsonify({"success": True, "reason": "User created successfully."})
        else:
            print("Transaction failed! User was not created.")
            return jsonify({"success": False, "reason": "Transaction failed."})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})
    
@login_bp.route('/checkface', methods=['POST'])
def run_face_recognition():
    try:
        # Receive JSON data
        print("Trying face recognition...")
        data = request.get_json()
        img_array = data.get("faceArray")

        #make sure three images were passed
        if(len(img_array) != 3):
            return jsonify({"success": False, "reason": "Please send exactly three images for facial recognition."})
        
        face_recognition_output = []
        face_recognition_output_images_only = []

        #first, check the three images to make sure only one face is detected in them
        for index, img in enumerate(img_array):
            result = scan_image_for_face(img)

            if result.get("success") == False:
                if "No face detected" in result.get("reason"):
                    return jsonify({"success": False, "reason": "No face detected in image " + str((index + 1)) +". Please try again."})
                if "Too many faces detected" in result.get("reason"):
                    return jsonify({"success": False, "reason": "Too many faces detected in image " + str((index + 1)) +". Please try again (only one face should be present)."})
                else:
                    return jsonify({"success": False, "reason": "Unknown error occurred."})
            else:
                print("Face recognition succeeded in image" + str(index + 1) + ".")
                face_recognition_output.append(result)
                face_recognition_output_images_only.append({"image": result.get("image")})
            
        return jsonify({"success": True, "reason": "OpenCV ran successfully and detected a face in all three photos.", "output": face_recognition_output_images_only})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})

@login_bp.route('/check-session', methods=['GET'])
def get_session():
    try:
        print("session data:", session)
        if "username" in session:
            return jsonify({
                "logged_in": True,
                "username": session["username"]
            })
        else:
            return jsonify({"logged_in": False})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})

@login_bp.route('/logoff-session', methods=['GET'])
def destroy_session():
    try:
        session.clear() #Logs out the user and destroys session
        return jsonify({"success": True})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})

#this decorator can be placed over Flask routes to protect them
#it will ensure that a proper login session is available before running a route!
def login_required(f):
    """Decorator to protect routes that require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return jsonify({"error": "Unauthorized"}), 401  # 🔹 Return 401 if no session
        session.permanent = True
        return f(*args, **kwargs)  # 🔹 Proceed if user is authenticated
    return decorated_function