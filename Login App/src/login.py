from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import os
import json
from web3 import Web3
import hashlib
import time
import cv2
import numpy as np
import base64
from PIL import Image
import imagehash
import io

login_bp = Blueprint('login', __name__, template_folder='templates')

# Load OpenCV's pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Configurations
ALCHEMY_API_URL = "https://eth-sepolia.g.alchemy.com/v2/Dv7X6LhBni2gxlcUzAPs51cKqdUHK-8Y"
CONTRACT_ADDRESS = "0x3C3bdFF7bab928680869E1377a63A957938dc4ce"
PRIVATE_KEY = "9ea2167fb16f55f70f2afca8644f9903b8f05f45c6268cf5c435b5df777c82a5"  # Owner's private key, need to delete later
#need to set up dotenv
#PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # Owner's private key

abi_file_path = os.path.abspath("../BlockChain/artifacts/contracts/FaceGuard.sol/FaceGuard.json")
print(f"Loading ABI from: {abi_file_path}")

with open(abi_file_path, "r") as f:
    abiJSONContent = json.load(f)

CONTRACT_ABI = abiJSONContent["abi"]

# Connect to Sepolia
w3 = Web3(Web3.HTTPProvider(ALCHEMY_API_URL))

if w3.is_connected() == True:
    print("W3 Connection to contract successful!")
else:
    print("W3 connection failed!")
    exit

#if script connected, we should be able to load contract into variable
# Load contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

#to interact with the contract, we have to prove we are the owners by using the private key of the wallet that deployed the contract
owner_account = w3.eth.account.from_key(PRIVATE_KEY)
owner_address = owner_account.address
w3.eth.default_account = owner_address

#a list to hold users temporarily while they are trying to 2FA, so we don't have to query the blockchain every time.
temporary_user_storage = []

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

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    else:
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
            
@login_bp.route('/login-2FA-Face', methods=['POST'])
def check_face_for_2FA():
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
    
    #get pHashes from user object
    reconstructed_hashes = []
    for solidity_bytes in user_obj[2]:
        # get hex string from bytes
        solidity_hex = solidity_bytes.hex()

        # Convert hex string to an integer
        phash_int = int(solidity_hex, 16)

        # Convert integer to a 64-bit binary string
        phash_bin = format(phash_int, '064b')  # Ensure 64 bits

        # Convert binary string to a NumPy boolean array
        phash_array = np.array([bool(int(b)) for b in phash_bin]).reshape((8, 8))  # 8x8 array

        reconstructed_hashes.append(imagehash.ImageHash(phash_array))  # Convert to ImageHash

    #finally, compare hamming distance of three detected faces for similarity comparison.
    hamming_distance_limit = 12

    for frameIndex, frameToScan in enumerate(frames):
        #need to make sure frame is not empty before trying to scan it
        if(frameToScan is None) or (frameToScan == ""):
            continue

        frameResult = scan_image_for_face(frameToScan)
        if frameResult["success"]:
            print("Comparing user PHashes with frame " + str(frameIndex) + "...")
            for hashIndex, userHash in enumerate(reconstructed_hashes):
                hamming_distance = (userHash - frameResult["hash"])
                print("Hamming Distance [Frame " + str(frameIndex) + " vs User PHash " + str(hashIndex) + "]: " + str(hamming_distance))
                if hamming_distance <= hamming_distance_limit:
                    print("Hamming distance below limit. Returning success...")
                    return jsonify({"success": True, "reason": "Face verified successfully."})
    
    return jsonify({"success": False, "reason": "User's face not detected."})

@login_bp.route('/usernamecheck', methods=['POST'])
def check_sent_username():
    data = request.get_json()
    username = data.get("username")
    
    result = check_username_exists(username)
    time.sleep(1)
    if result == True:
        return jsonify({"success": False, "reason": "ERROR: Username already exists on the smart contract! Please create a unique username to continue."})
    else:
        return jsonify({"success": True, "reason": "Username is available."})

@login_bp.route('/signup', methods=['POST'])
def signup():
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
        result = scan_image_for_face(img)
        if result["success"]:
            face_image_data.append(result)
        else:
            return jsonify ({"success": False, "reason": result["reason"]})
        
    print("Face hashes obtained.")

    #we have to convert the phash array to a hex string so it can be stored in solidity
    imagehash_phash_hex_array = []
    for result in face_image_data:
        # Convert pHash to bytes
        phash_int = int(result["hash_string"], 16)  # Convert pHash to integer from hex
        # Convert to a compact hex string
        phash_hex = format(phash_int, '016x')  # Ensures it's always 16 characters (64 bits)
        phash_hex = "0x" + phash_hex  # Prefix with '0x' for Solidity compatibility

        print(phash_hex)  # Example Output: 0xabcdef1234567890
        imagehash_phash_hex_array.append(phash_hex)

    print("Estimating gas...")
    #estimate the cost of the ethereum transaction by predicting gas
    estimated_gas = contract.functions.registerUser(username, password, imagehash_phash_hex_array, "testing_GUID").estimate_gas({"from": owner_address})

    #register user (use estimated gas & add an extra 50000 buffer to make sure transaction goes through)
    tx = contract.functions.registerUser(
        username, password, imagehash_phash_hex_array, "testing_GUID"
    ).build_transaction({
        "from": owner_address,
        "nonce": w3.eth.get_transaction_count(owner_address),
        "gas": estimated_gas + 50000, 
        "gasPrice": w3.to_wei("10", "gwei")
    })

    # Sign transaction with private key
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)

    # Send transaction to blockchain
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    # Wait for confirmation of transaction
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Print transaction status
    if receipt.status == 1:
        print(f"Transaction successful! Block: {receipt.blockNumber}")
        print("Waiting a few more seconds...")
        time.sleep(15)

        print("Checking to see if user exists now...")
        user_obj = contract.functions.getUser(username).call()
        print(user_obj)
        if user_obj[0] == "":
            userExists = False
            #this should not happen if transaction went through
            print("The transaction went through but the user is still not found. It will show up eventually I guess")
        else:
            userExists = True
            print("The user is now on the blockchain! The script was successful.")
            return jsonify({"success": True, "reason": "User created successfully."})
    else:
        print("Transaction failed! User was not created.")
        return jsonify({"success": False, "reason": "Transaction failed."})
    
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
        """
        preview_padding = 15  # Adjustable padding for preview image
        face_padding = 5 #padding for cropping face in image to generate pHash

        # Ensure the expanded crop does not exceed image boundaries
        x_start_preview = max(x - preview_padding, 0)
        y_start_preview = max(y - preview_padding, 0)
        x_end_preview = min(x + w + preview_padding, img.shape[1])
        y_end_preview = min(y + h + preview_padding, img.shape[0])

        # Ensure the face-only crop does not exceed image boundaries
        x_start = max(x - face_padding, 0)
        y_start = max(y - face_padding, 0)
        x_end = min(x + w + face_padding, img.shape[1])
        y_end = min(y + h + face_padding, img.shape[0])

        #make copy of img variable before drawing square, so the green square does not appear in the face-only crop photo
        img_copy = img.copy()
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Crop the face with padding, makes preview image and actual face-only image that will be used to generate pHash
        face_crop = img[y_start_preview:y_end_preview, x_start_preview:x_end_preview]
        face_only_crop = img_copy[y_start:y_end, x_start:x_end]

        _, buffer = cv2.imencode('.png', face_only_crop)
        face_base64_img = base64.b64encode(buffer).decode('utf-8')

        #draw green square on preview image
        cv2.rectangle(face_crop, (x, y), (x + w, y + h), (0, 255, 0), 2)

        _, buffer = cv2.imencode('.png', face_crop)
        preview_base64_img = base64.b64encode(buffer).decode('utf-8')

        """

        img_copy = img.copy()

        #draw rectangle on image
        cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)

        _, buffer = cv2.imencode('.png', img)
        face_base64_img = base64.b64encode(buffer).decode('utf-8')

        _, buffer = cv2.imencode('.png', img_copy)
        face_preview_base64_img = base64.b64encode(buffer).decode('utf-8')

        # Generate hash for the face from the original image
        face_hash = perceptual_hash_from_base64(face_base64_img)
        face_hash_string = str(face_hash)

        return {"success": True, "reason": "OpenCV ran successfully on provided image.", "hash": face_hash, "hash_string": face_hash_string, "image": face_preview_base64_img}
    
@login_bp.route('/checkface', methods=['POST'])
def run_face_recognition():
    #try:
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

"""
    #finally, compare hamming distance of three detected faces for similarity comparison.
    hamming_distance_limit = 5
    hamming_distance_failed = False

    for face_output in face_recognition_output:
        for inner_face_ouput in face_recognition_output:
            print("Comparing PHash: " + face_output.get("hash_string") + " to " + inner_face_ouput.get("hash_string"))
            hamming_distance = (face_output.get("hash") - inner_face_ouput.get("hash"))
            print("Hamming Distance: " + str(hamming_distance) + ".")
            if hamming_distance > hamming_distance_limit:
                print("Hamming Distance exceeds allowed limit. Face comparison failed.")
                hamming_distance_failed = True

    if hamming_distance_failed:
        return jsonify({"success": False, "reason": "OpenCV ran successfully, but faces found in three photos do not match. Please ensure they are as similar as possible."})
    else:
        #need to take out imagehash from array because it is not JSON serializable
        final_face_recognition_return_array = []

        for output in face_recognition_output:
            final_face_recognition_return_array.append({"hash": output.get("hash_string"), "image": output.get("image")})

        return jsonify({"success": True, "reason": "OpenCV ran successfully. Face similarity check passed between three photos.", "output": final_face_recognition_return_array})
    
    return False

    # Decode Base64 back to an image
    img_data = base64.b64decode(img_base64)
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Convert to grayscale for better face detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    faces_list = []

    for (x, y, w, h) in faces:
        padding = 50  # Increase this value for a larger margin

        # Ensure the new coordinates are within the image boundaries
        x_start = max(x - padding, 0)
        y_start = max(y - padding, 0)
        x_end = min(x + w + padding, img.shape[1])
        y_end = min(y + h + padding, img.shape[0])

        # Crop the face with extra space
        face_crop = img[y_start:y_end, x_start:x_end]

        # Encode the detected face with bounding box to Base64 (PNG)
        _, detected_face_img_encoded = cv2.imencode('.png', face_crop)
        face_img_base64_out = base64.b64encode(detected_face_img_encoded).decode('utf-8')

        # Generate hash for the face
        face_hash = perceptual_hash_from_base64(face_img_base64_out)
        print(face_hash)

        # Draw rectangle around face
        cv2.rectangle(face_crop, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Encode the final image with bounding box to Base64
        _, img_encoded = cv2.imencode('.png', img)
        img_base64_out = base64.b64encode(img_encoded).decode('utf-8')

        faces_list.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h), "hash": face_hash})
    

    # Return face coordinates
    faces_list = [{"x": int(x), "y": int(y), "w": int(w), "h": int(h)} for (x, y, w, h) in faces]

    if len(faces_list) < 1:
        return jsonify({"success": False, "reason": "No face detected in image!"})
    if len(faces_list) > 1:
        return jsonify({"success": False, "reason": "Two or more faces detected! Only one face should be uploaded."})
    
    return jsonify({"success": True, "reason": "OpenCV ran successfully.", "faces_detected": len(faces_list), "faces": faces_list, "image": face_img_base64_out, "hamming_distance": hash1 - hash2})
    #except Exception as e:
        #return jsonify({"success": False, "reason": str(e)})
        """