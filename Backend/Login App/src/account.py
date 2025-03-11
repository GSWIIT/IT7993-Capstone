from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from web3 import Web3
import os
import json
from login import login_required
from functools import wraps
from blockchain_connection import get_contract, get_w3_object, get_owner_address, get_private_key
import time
from login import hash_password, create_lsh_from_image

account_bp = Blueprint('account', __name__, template_folder='templates')

contract = get_contract()
w3 = get_w3_object()
owner_address = get_owner_address()
PRIVATE_KEY = get_private_key()

#protected with login_required decorator function
@account_bp.route('/get-self', methods=['GET'])
@login_required
def get_self():
    #get user permissions first
    permissions = contract.functions.getUserPermissions(session["username"]).call()

    has_read_self = any("FaceGuard Read: Self" in perm for perm in permissions)

    if(has_read_self):
        user = contract.functions.getUser(session["username"]).call()
        return jsonify ({"success": True, "reason": "User retrieved successfully.", "user": user})
    else:
        return jsonify ({"success": False, "reason": "User does not have permission to perform this action.", "user": None})
    
#protected with login_required decorator function
@account_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json()
    email = data.get("email")
    fullName = data.get("fullName")

    emailUpdated = False
    fullNameUpdated = False

    #get user permissions first
    permissions = contract.functions.getUserPermissions(session["username"]).call()

    has_read_self = any("FaceGuard Read: Self" in perm for perm in permissions)

    if has_read_self:
        user = contract.functions.getUser(session["username"]).call()
        print(user[7], user[8])
        if(user[7] != email):
            emailUpdated = True

        if(user[8] != fullName):
            fullNameUpdated = True

        if(emailUpdated):
            print("Email needs to be updated. Estimating gas...")
            try:
                estimated_gas = contract.functions.updateUserEmail(session["username"], email).estimate_gas({"from": owner_address})
            except Exception as e:
                return jsonify ({"success": False, "reason": "Error encountered! Blockchain Response[" + str(e.args[0]) + "]."})

            # Get the suggested gas price
            gas_price = w3.eth.gas_price  # Fetch the current network gas price dynamically
            max_priority_fee = w3.to_wei("4", "gwei")  # Priority fee (adjust based on congestion)
            max_fee_per_gas = gas_price + max_priority_fee

            tx = contract.functions.updateUserEmail(session["username"], email).build_transaction({
                "from": owner_address,
                "nonce": w3.eth.get_transaction_count(owner_address),
                "gas": estimated_gas + 200000, 
                "maxFeePerGas": max_fee_per_gas,  # Total fee
                "maxPriorityFeePerGas": max_priority_fee,  # Tip for miners
            })

            # Sign transaction with private key
            signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)

            print("Sending group name update transaction...")
            # Send transaction to blockchain
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Wait for confirmation of transaction
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            # Print transaction status
            if receipt.status == 1:
                print("Updated user email successfully.")

        if(fullNameUpdated):
            print("Full name needs to be updated. Estimating gas...")
            try:
                estimated_gas = contract.functions.updateUserFullName(session["username"], fullName).estimate_gas({"from": owner_address})
            except Exception as e:
                return jsonify ({"success": False, "reason": "Error encountered! Blockchain Response[" + str(e.args[0]) + "]."})

            # Get the suggested gas price
            gas_price = w3.eth.gas_price  # Fetch the current network gas price dynamically
            max_priority_fee = w3.to_wei("4", "gwei")  # Priority fee (adjust based on congestion)
            max_fee_per_gas = gas_price + max_priority_fee

            tx = contract.functions.updateUserFullName(session["username"], fullName).build_transaction({
                "from": owner_address,
                "nonce": w3.eth.get_transaction_count(owner_address),
                "gas": estimated_gas + 200000, 
                "maxFeePerGas": max_fee_per_gas,  # Total fee
                "maxPriorityFeePerGas": max_priority_fee,  # Tip for miners
            })

            # Sign transaction with private key
            signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)

            print("Sending group name update transaction...")
            # Send transaction to blockchain
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Wait for confirmation of transaction
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            # Print transaction status
            if receipt.status == 1:
                print("Updated user full name successfully.")

    return jsonify ({"success": True, "reason": "Request completed successfully!"})

#protected with login_required decorator function
@account_bp.route('/update-password', methods=['POST'])
@login_required
def update_password():
    data = request.get_json()
    password = data.get("password")

    #get user permissions first
    permissions = contract.functions.getUserPermissions(session["username"]).call()

    has_update_self = any("FaceGuard Read: Self" in perm for perm in permissions)

    if has_update_self:
        password = hash_password(password)

        print("Password needs to be updated. Estimating gas...")
        try:
            estimated_gas = contract.functions.updateUserPassword(session["username"], password).estimate_gas({"from": owner_address})
        except Exception as e:
            return jsonify ({"success": False, "reason": "Error encountered! Blockchain Response[" + str(e.args[0]) + "]."})

        # Get the suggested gas price
        gas_price = w3.eth.gas_price  # Fetch the current network gas price dynamically
        max_priority_fee = w3.to_wei("4", "gwei")  # Priority fee (adjust based on congestion)
        max_fee_per_gas = gas_price + max_priority_fee

        tx = contract.functions.updateUserPassword(session["username"], password).build_transaction({
            "from": owner_address,
            "nonce": w3.eth.get_transaction_count(owner_address),
            "gas": estimated_gas + 200000, 
            "maxFeePerGas": max_fee_per_gas,  # Total fee
            "maxPriorityFeePerGas": max_priority_fee,  # Tip for miners
        })

        # Sign transaction with private key
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)

        print("Sending password update transaction...")
        # Send transaction to blockchain
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Wait for confirmation of transaction
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        # Print transaction status
        if receipt.status == 1:
            print("Updated user password successfully.")
            return jsonify ({"success": True, "reason": "Password updated successfully!"})
        else:
            return jsonify ({"success": False, "reason": "There was an issue writing to the blockchain..."})
    else:
        return jsonify ({"success": False, "reason": "User does not have permission to peform this action!"})
    
#protected with login_required decorator function
@account_bp.route('/update-face-hashes', methods=['POST'])
@login_required
def update_face_hashes():
    data = request.get_json()
    faceArray = data.get("faceArray")

    #get user permissions first
    permissions = contract.functions.getUserPermissions(session["username"]).call()

    has_update_self = any("FaceGuard Read: Self" in perm for perm in permissions)

    if has_update_self:
        #get face hash data from images. This also verifies that the photos actually have faces in them.
        face_image_data = []
        for img in faceArray:
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

        print("Face hashes need to be updated. Estimating gas...")
        try:
            estimated_gas = contract.functions.updateUserFaceHash(session["username"], face_hash_array).estimate_gas({"from": owner_address})
        except Exception as e:
            return jsonify ({"success": False, "reason": "Error encountered! Blockchain Response[" + str(e.args[0]) + "]."})

        # Get the suggested gas price
        gas_price = w3.eth.gas_price  # Fetch the current network gas price dynamically
        max_priority_fee = w3.to_wei("4", "gwei")  # Priority fee (adjust based on congestion)
        max_fee_per_gas = gas_price + max_priority_fee

        tx = contract.functions.updateUserFaceHash(session["username"], face_hash_array).build_transaction({
            "from": owner_address,
            "nonce": w3.eth.get_transaction_count(owner_address),
            "gas": estimated_gas + 200000, 
            "maxFeePerGas": max_fee_per_gas,  # Total fee
            "maxPriorityFeePerGas": max_priority_fee,  # Tip for miners
        })

        # Sign transaction with private key
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)

        print("Sending face hash update transaction...")
        # Send transaction to blockchain
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Wait for confirmation of transaction
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        # Print transaction status
        if receipt.status == 1:
            print("Updated user face hashes successfully.")
            return jsonify ({"success": True, "reason": "Password updated successfully!"})
        else:
            return jsonify ({"success": False, "reason": "There was an issue writing to the blockchain..."})
    else:
        return jsonify ({"success": False, "reason": "User does not have permission to peform this action!"})