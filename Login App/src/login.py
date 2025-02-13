from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import os
import json
from web3 import Web3
import hashlib
import time

login_bp = Blueprint('login', __name__, template_folder='templates')

def hash_password(password: str) -> str:
    """Simulates hashing of password (should match how it's stored in contract)."""
    return hashlib.sha256(password.encode()).hexdigest()

#this function checks the smart contract to see if a username already exists
def check_username_exists(username):
    user_obj = contract.functions.getUser(username).call()
    print(user_obj)
    if user_obj[0] == "":
        print("Username does not exist in system yet.")
        return False
    else:
        print("Username exists in system already!")
        return True

# Configurations
ALCHEMY_API_URL = "https://eth-sepolia.g.alchemy.com/v2/Dv7X6LhBni2gxlcUzAPs51cKqdUHK-8Y"
CONTRACT_ADDRESS = "0x427461725DD56ed90fB89101B2434D760D601ecb"
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

#if script connected and did not exit, we should be able to load contract into variable
# Load contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

#to interact with the contract, we have to prove we are the owners by using the private key of the wallet that deployed the contract
owner_account = w3.eth.account.from_key(PRIVATE_KEY)
owner_address = owner_account.address
w3.eth.default_account = owner_address

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


@login_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    result = check_username_exists(username)

    time.sleep(5)

    if result == True:
        return jsonify({"success": False, "reason": "ERROR: Username already exists on the smart contract! Please create a unique username to continue."})
    
    password = hash_password(password)

    #estimate the cost of the ethereum transaction by predicting gas
    estimated_gas = contract.functions.registerUser(username, password, "testing", "testing_GUID").estimate_gas({"from": owner_address})

    #register user (use estimated gas & add an extra 50000 buffer to make sure transaction goes through)
    tx = contract.functions.registerUser(
        username, password, "testing", "testing_GUID"
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