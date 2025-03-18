from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from web3 import Web3
import os
import json
from login import login_required
from functools import wraps
from blockchain_connection import get_contract, get_w3_object, get_owner_address, get_private_key, CONTRACT_ADDRESS
import time
from login import hash_password, create_lsh_from_image
from hexbytes import HexBytes  # Import this for type checking
import datetime

account_bp = Blueprint('account', __name__, template_folder='templates')

contract = get_contract()
w3 = get_w3_object()
owner_address = get_owner_address()
PRIVATE_KEY = get_private_key()

class HexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        return super().default(obj)

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
            return jsonify ({"success": True, "reason": "Facial Recognition updated successfully!"})
        else:
            return jsonify ({"success": False, "reason": "There was an issue writing to the blockchain..."})
    else:
        return jsonify ({"success": False, "reason": "User does not have permission to peform this action!"})
    
def convert_attr_dict(obj):
    if isinstance(obj, list):
        return [convert_attr_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_attr_dict(value) for key, value in obj.items()}
    elif isinstance(obj, bytes):  
        return HexBytes.to_hex(obj)  # Convert bytes to hex string for JSON compatibility
    return obj  # Return unchanged if not AttributeDict, list, or dict

def get_web3_event_logs_from_username(event, username_topic):
    # Collect all user's events into an array
    all_events = []

    event_obj = event()

    signature = Web3.keccak(text=event.signature).hex()

    logs = w3.eth.get_logs({
        'fromBlock': 'earliest',
        'toBlock': 'latest',
        'address': contract.address,
        'topics': ["0x" + signature, "0x" + username_topic]  # Must match indexed parameters
    })

    for log in logs:
        decoded_event = event_obj.process_log(log)
        all_events.append(decoded_event)

    #json_result = ([w3.to_json(log) for log in all_events])

    return all_events

#protected with login_required decorator function
@account_bp.route('/get-user-events', methods=['GET'])
@login_required
def get_user_events():
    try:
        username_logs_requested = request.args.get('username')  # Retrieve the username from query parameters
    except:
        print("No username sent. Assuming session user logs will be sent.")
        username_logs_requested = None

    permissions = contract.functions.getUserPermissions(session["username"]).call()

    has_read_all = any("FaceGuard Read: All" in perm for perm in permissions)
    has_read_users = any("FaceGuard Read: Users" in perm for perm in permissions)
    has_read_self = any("FaceGuard Read: Self" in perm for perm in permissions)

    return_allowed = False

    if has_read_all or has_read_users:
        return_allowed = True
    else:
        if has_read_self:
            if username_logs_requested != None:
                if (username_logs_requested == session["username"]):
                    return_allowed = True
                else:
                    return_allowed = False
            else:
                return_allowed = True

    if(return_allowed == False):
        return jsonify ({"success": False, "reason": "User does not have permission to perform this action!"})
    
    if(username_logs_requested != None):
        username = username_logs_requested
    else:
        username = session["username"]

    #list events to check for on the blockchain
    events = [
        contract.events.UserRegistered,
        contract.events.UserLoggedIn,
        contract.events.PasswordUpdated,
        contract.events.PasswordChangeRequired,
        contract.events.FaceHashUpdated,
        contract.events.UserEmailUpdated,
        contract.events.UserFullNameUpdated,
        contract.events.UserToggled,
        contract.events.UserAddedToGroup,
        contract.events.UserRemovedFromGroup
    ]

    # Convert the username to a topic (if indexed)
    username_topic = w3.keccak(text=username).hex()

    #we will format the logs to return them to the FaceGuard app
    all_formatted_logs = []

    for event in events:
        event_logs = get_web3_event_logs_from_username(event, username_topic)

        for log in event_logs:
            block_number = int(log["blockNumber"])
            block_timestamp = w3.eth.get_block(block_number).timestamp
            formatted_timestamp = datetime.datetime.fromtimestamp(block_timestamp)

            event_name = log["event"]
            event_data = f"User [{username}] "
            match event_name:
                case "UserRegistered":
                    event_data += "successfully registered to smart contract."
                case "UserLoggedIn":
                    event_data += "authenticated successfully."
                case "PasswordUpdated":
                    event_data += "updated password successfully."
                case "PasswordChangeRequired":
                    event_data += "updated. An admin has required this account to update their password on next login."
                case "FaceHashUpdated":
                    event_data += "uploaded new face hashes successfully."
                case "UserEmailUpdated":
                    log_old_email = log["args"]["oldEmail"]
                    if log_old_email == "":
                        log_old_email = "' '"
                    log_new_email = log["args"]["newEmail"]
                    event_data += f"updated email address successfully ([{log_old_email} => {log_new_email}])."
                case "UserFullNameUpdated":
                    log_old_full_name = log["args"]["oldFullName"]
                    if log_old_full_name == "":
                        log_old_full_name = "' '"
                    log_new_full_name = log["args"]["newFullName"]
                    event_data += f"updated full name successfully ([{log_old_full_name} => {log_new_full_name}])."
                case "UserToggled":
                    log_enabled = log["args"]["enabled"]
                    if log_enabled:
                        event_data += "account has been enabled."
                    else:
                        event_data += "account has been disabled."
                case "UserAddedToGroup":
                    log_group_name = log["args"]["groupName"]
                    event_data += f"added to permissions group successfully ([{log_group_name}])."
                case "UserRemovedFromGroup":
                    log_group_name = log["args"]["groupName"]
                    event_data += f"removed from permissions group successfully ([{log_group_name}])."
                case _:
                    event_data += "[Server Error: Event Not Implemented.]"
            
            all_formatted_logs.append({"timestamp": formatted_timestamp, "block": block_number, "event": event_name, "data": event_data})            

    all_formatted_logs.sort(key=lambda log: log["timestamp"], reverse=True)

    return jsonify ({"success": True, "reason": "Obtained user events successfully.", "logs": all_formatted_logs})

#protected with login_required decorator function
@account_bp.route('/delete-self', methods=['GET'])
@login_required
def delete_self():
    permissions = contract.functions.getUserPermissions(session["username"]).call()

    has_delete_all = any("FaceGuard Delete: All" in perm for perm in permissions)
    has_delete_users = any("FaceGuard Delete: Users" in perm for perm in permissions)
    has_delete_self = any("FaceGuard Delete: Self" in perm for perm in permissions)

    if has_delete_all or has_delete_users or has_delete_self:
        print("User will be deleted. Estimating gas...")
        try:
            estimated_gas = contract.functions.removeUser(session["username"]).estimate_gas({"from": owner_address})
        except Exception as e:
            return jsonify ({"success": False, "reason": "Error encountered! Blockchain Response[" + str(e.args[0]) + "]."})

        # Get the suggested gas price
        gas_price = w3.eth.gas_price  # Fetch the current network gas price dynamically
        max_priority_fee = w3.to_wei("4", "gwei")  # Priority fee (adjust based on congestion)
        max_fee_per_gas = gas_price + max_priority_fee

        tx = contract.functions.removeUser(session["username"]).build_transaction({
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
            return jsonify ({"success": True, "reason": "User deleted successfully."})
        else:
            return jsonify ({"success": False, "reason": "An error occurred while writing to the blockchain..."})