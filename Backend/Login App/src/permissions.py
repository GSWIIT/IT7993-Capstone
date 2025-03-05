from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from web3 import Web3
import os
import json
from login import login_required
from functools import wraps

permissions_bp = Blueprint('permissions', __name__, template_folder='templates')

# Configurations
ALCHEMY_API_URL = "https://eth-sepolia.g.alchemy.com/v2/Dv7X6LhBni2gxlcUzAPs51cKqdUHK-8Y"
CONTRACT_ADDRESS = "0xbe27997a7d178235f54cB499A459D3c6978F745E"
PRIVATE_KEY = "9ea2167fb16f55f70f2afca8644f9903b8f05f45c6268cf5c435b5df777c82a5"  # Owner's private key, need to delete later
#need to set up dotenv
#PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # Owner's private key

abi_file_path = os.path.abspath("./BlockChain/artifacts/contracts/FaceGuard.sol/FaceGuard.json")
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

#protected with login_required decorator function
@permissions_bp.route('/get-users', methods=['GET'])
@login_required
def get_all_users():
    usernames = contract.functions.getAllUsernames().call()

    all_users_array = []

    for username in usernames:
        user = contract.functions.getUser(username).call()
        face_hashes_exist = False

        if user[2] is not None:
            face_hashes_exist = True

        all_users_array.append({
            "username": user[0], 
            "faceHashes": face_hashes_exist,
            "assignedGroups": user[3],
            "accountCreationDate": user[4],
            "lastEditDate": user[5],
            "faceReenrollmentRequired": user[6],
            "enabled": user[7]
        })


    return jsonify({"success": True, "reason": "Testing successful.", "array": all_users_array})