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
from imagehash import dhash
import io
import face_recognition
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from datasketch import MinHash
import pickle
import hashlib
from collections import Counter

login_bp = Blueprint('login', __name__, template_folder='templates')

# Load OpenCV's pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
face_hash_secret_key = "Anthony123!!!!!!".encode() #for testing only

# Configurations
ALCHEMY_API_URL = "https://eth-sepolia.g.alchemy.com/v2/Dv7X6LhBni2gxlcUzAPs51cKqdUHK-8Y"
CONTRACT_ADDRESS = "0xC8C34F83d6B15a9d3043B6A5a9b2E79926b2A94E"
PRIVATE_KEY = "9ea2167fb16f55f70f2afca8644f9903b8f05f45c6268cf5c435b5df777c82a5"  # Owner's private key, need to delete later
#need to set up dotenv
#PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # Owner's private key

abi_file_path = os.path.abspath("../../BlockChain/artifacts/contracts/FaceGuard.sol/FaceGuard.json")
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

NUM_PERM = 128  # Ensure the same number of permutations throughout

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
    
#for generating Locality-Sensitive Hashing (LSH) values for face embeddings
def generate_random_hyperplanes(num_planes, dimension):
    # Generates random hyperplanes for the LSH transformation
    return np.random.randn(num_planes, dimension)

def lsh_embedding(embedding, hyperplanes):
    # Projects the embedding onto each hyperplane and thresholds to generate a binary vector
    projection = np.dot(hyperplanes, embedding)
    binary_hash = projection > 0  # Boolean array: True if positive, False otherwise
    return binary_hash.astype(int)

def binary_string_to_int_array(binary_str):
    return np.array(list(binary_str), dtype=int)

def hamming_distance(str1, str2):
    return sum(b1 != b2 for b1, b2 in zip(str1, str2))

def create_lsh_hash(embedding, num_perm=NUM_PERM):
    """Converts a face embedding into an LSH-compatible MinHash object."""
    m = MinHash(num_perm=num_perm)
    for value in embedding:
        m.update(str(value).encode('utf8'))  # Ensure encoding is consistent
    return m

def minhash_to_flat_uint256_array(minhash_list):
    """Flattens multiple MinHashes into a single uint256[] array for Solidity storage."""
    flat_array = []
    for minhash in minhash_list:
        flat_array.extend(minhash.hashvalues.tolist())  # Convert to Python list explicitly
    return flat_array

def flat_uint256_array_to_minhash_list(flat_array, num_perm=NUM_PERM):
    """Reconstructs a list of MinHash objects from a flat uint256 array."""
    num_hashes = len(flat_array) // num_perm  # Determine number of MinHash objects
    minhash_list = []

    for i in range(num_hashes):
        m = MinHash(num_perm=num_perm)
        m.hashvalues = np.array(flat_array[i * num_perm:(i + 1) * num_perm], dtype=np.uint64)
        minhash_list.append(m)

    return minhash_list

def compare_lsh_hashes(hash1, hash2):
    """Compares two MinHash objects using Jaccard similarity."""
    return hash1.jaccard(hash2)

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

def compare_face_hashes(new_encoding, stored_hash):
    """ Compare hashes using Hamming Distance """
    new_hash = hash_face_encoding(new_encoding)  # Generate new hash

    # Compute Hamming Distance
    distance = hamming_distance(new_hash, stored_hash)

    print("Distance between hashes: " + str(distance))

    # Set threshold (adjust based on testing)
    return distance < 10  # Lower value means closer match

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

    #finally, compare euclidean distance of three detected faces for similarity comparison.
    hamming_distance_limit = 4

    for frameIndex, frameToScan in enumerate(frames):
        #need to make sure frame is not empty before trying to scan it
        if(frameToScan is None) or (frameToScan == ""):
            continue

        frameEncoding = create_lsh_from_image(frameToScan)
        
        if frameEncoding["success"]:
            print("Comparing face embeddings with frame " + str(frameIndex) + "...")
            for hashIndex, userHash in enumerate(user_obj[2]):
                # Compute Euclidean distance
                print(frameEncoding["hash"])
                print(userHash)
                results = hamming_distance(frameEncoding["hash"], userHash)
                print("Hamming distance [Frame " + str(frameIndex) + " vs User LSH " + str(hashIndex) + "]: " + str(results))
                if results <= hamming_distance_limit:
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

    #print(face_hash_array)
    #face_minhash_flat_array = minhash_to_flat_uint256_array(face_hash_array)
    #print("flattened array")
    #print(face_minhash_flat_array)

    """
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
    """

    print("Estimating gas...")
    #estimate the cost of the ethereum transaction by predicting gas
    estimated_gas = contract.functions.registerUser(username, password, face_hash_array, "testing_GUID").estimate_gas({"from": owner_address})

    # Get the suggested gas price
    gas_price = w3.eth.gas_price  # Fetch the current network gas price dynamically
    max_priority_fee = w3.to_wei("2", "gwei")  # Priority fee (adjust based on congestion)
    max_fee_per_gas = gas_price + max_priority_fee

    #register user (use estimated gas & add an extra 50000 buffer to make sure transaction goes through)
    tx = contract.functions.registerUser(
        username, password, face_hash_array, "testing_GUID"
    ).build_transaction({
        "from": owner_address,
        "nonce": w3.eth.get_transaction_count(owner_address),
        "gas": estimated_gas + 200000, 
        "maxFeePerGas": max_fee_per_gas,  # Total fee
        "maxPriorityFeePerGas": max_priority_fee,  # Tip for miners
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
        face_region = img[y:y+h, x:x+w]

        # Convert the face region from BGR to RGB
        face_region_rgb = cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB)

        # Get face encodings from the cropped face region
        encodings = face_recognition.face_encodings(img)
        if encodings:
            face_encoding = encodings[0]
            print("Face encoding obtained.")
        else:
            print("No face encoding found.")
            return {"success": False, "reason": "No face encoding found."}

        lsh_hash_obj = hash_face_encoding(face_encoding)
        
        return {"success": True, "reason": "OpenCV ran successfully. Face embedding created and hashed successfully.", "hash": lsh_hash_obj, "encoding": lsh_hash_obj}
    
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