from flask import Blueprint, request, session, jsonify
from web3 import Web3
from login import login_required
from blockchain_connection import get_contract, get_w3_object, write_to_blockchain
from login import hash_password, create_lsh_from_image
from permissions import check_if_user_has_permission
from hexbytes import HexBytes  # Import this for type checking
import datetime

account_bp = Blueprint('account', __name__, template_folder='templates')

contract = get_contract()
w3 = get_w3_object()

def convert_attr_dict(obj):
    if isinstance(obj, list):
        return [convert_attr_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_attr_dict(value) for key, value in obj.items()}
    elif isinstance(obj, bytes):  
        return HexBytes.to_hex(obj)  # Convert bytes to hex string for JSON compatibility
    return obj  # Return unchanged if not AttributeDict, list, or dict

"""
def get_web3_event_logs_from_topic(event, topic):
    # Collect all user's events into an array
    all_events = []

    event_obj = event()

    signature = Web3.keccak(text=event.signature).hex()

    logs = w3.eth.get_logs({
        'fromBlock': 'earliest',
        'toBlock': 'latest',
        'address': contract.address,
        'topics': ["0x" + signature, "0x" + topic]  # Must match indexed parameters
    })

    for log in logs:
        decoded_event = event_obj.process_log(log)
        all_events.append(decoded_event)

    #json_result = ([w3.to_json(log) for log in all_events])

    return all_events
"""

def get_web3_event_logs_from_topic(event, topic=None):
    all_events = []
    event_obj = event()
    signature = Web3.keccak(text=event.signature).hex()

    # Build topics list
    topics = ["0x" + signature]  # topics[0] is always the signature
    topics.append("0x" + Web3.keccak(text=topic).hex()) #add indexed string to search for, as web3 encoded string

    logs = w3.eth.get_logs({
        'fromBlock': 'earliest',
        'toBlock': 'latest',
        'address': contract.address,
        'topics': topics
    })

    for log in logs:
        decoded_event = event_obj.process_log(log)
        all_events.append(decoded_event)

    return all_events

#protected with login_required decorator function
@account_bp.route('/get-self', methods=['GET'])
@login_required
def get_self():
    try:
        has_read_self = check_if_user_has_permission(session["username"], "FaceGuard Read: Self")

        if(has_read_self):
            user = contract.functions.getUser(session["username"]).call()
            return jsonify ({"success": True, "reason": "User retrieved successfully.", "user": user})
        else:
            return jsonify ({"success": False, "reason": "User does not have permission to perform this action.", "user": None})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: "  + str(e.args[0]) + "!"})
    
#protected with login_required decorator function
@account_bp.route('/get-self-group-links', methods=['GET'])
@login_required
def get_self_group_links():
    try:
        has_read_self = check_if_user_has_permission(session["username"], "FaceGuard Read: Self")

        if(has_read_self):
            user = contract.functions.getUser(session["username"]).call()
            return jsonify ({"success": True, "reason": "User retrieved successfully.", "user": user})
        else:
            return jsonify ({"success": False, "reason": "User does not have permission to perform this action.", "user": None})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: "  + str(e.args[0]) + "!"})  
    
#protected with login_required decorator function
@account_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    try:
        data = request.get_json()
        email = data.get("email")
        fullName = data.get("fullName")

        emailUpdated = False
        fullNameUpdated = False

        has_update_self = check_if_user_has_permission(session["username"], "FaceGuard Update: Self")

        if has_update_self:
            user = contract.functions.getUser(session["username"]).call()
            print(user[6], user[7])
            if(user[6] != email):
                emailUpdated = True

            if(user[7] != fullName):
                fullNameUpdated = True

            if(emailUpdated):
                print("Email needs to be updated...")
                transaction = write_to_blockchain(contract.functions.updateUserEmail, [session["username"], email])

                # Wait for confirmation of transaction
                receipt = w3.eth.wait_for_transaction_receipt(transaction)

                # Print transaction status
                if receipt.status == 1:
                    print("Updated user email successfully.")
                else:
                    raise Exception("ERROR: BlockChain failed to write transaction to blockchain!")

            if(fullNameUpdated):
                print("Full name needs to be updated...")
                transaction = write_to_blockchain(contract.functions.updateUserFullName, [session["username"], fullName])

                # Wait for confirmation of transaction
                receipt = w3.eth.wait_for_transaction_receipt(transaction)

                # Print transaction status
                if receipt.status == 1:
                    print("Updated user email successfully.")
                else:
                    raise Exception("ERROR: BlockChain failed to write transaction to blockchain!")

            return jsonify ({"success": True, "reason": "Request completed successfully!"})
        else:
            return jsonify ({"success": False, "reason": "User does not have permission to perform this action!"})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: "  + str(e.args[0]) + "!"})

#protected with login_required decorator function
@account_bp.route('/update-password', methods=['POST'])
@login_required
def update_password():
    try:
        data = request.get_json()
        password = data.get("password")

        has_update_self = check_if_user_has_permission(session["username"], "FaceGuard Update: Self")

        if has_update_self:
            password = hash_password(password)

            print("Password needs to be updated.")
            transaction = write_to_blockchain(contract.functions.updateUserPassword, [session["username"], password])

            # Wait for confirmation of transaction
            receipt = w3.eth.wait_for_transaction_receipt(transaction)

            # Print transaction status
            if receipt.status == 1:
                print("Updated user password successfully.")
                return jsonify ({"success": True, "reason": "Password updated successfully!"})
            else:
                return jsonify ({"success": False, "reason": "There was an issue writing to the blockchain..."})
        else:
            return jsonify ({"success": False, "reason": "User does not have permission to peform this action!"})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})
    
#protected with login_required decorator function
@account_bp.route('/update-face-hashes', methods=['POST'])
@login_required
def update_face_hashes():
    try:
        data = request.get_json()
        faceArray = data.get("faceArray")

        has_update_self = check_if_user_has_permission(session["username"], "FaceGuard Update: Self")

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

            print("Face hashes need to be updated...")
            transaction = write_to_blockchain(contract.functions.updateUserFaceHash, [session["username"], face_hash_array])

            # Wait for confirmation of transaction
            receipt = w3.eth.wait_for_transaction_receipt(transaction)

            # Print transaction status
            if receipt.status == 1:
                print("Updated user face hashes successfully.")
                return jsonify ({"success": True, "reason": "Facial Recognition updated successfully!"})
            else:
                return jsonify ({"success": False, "reason": "There was an issue writing to the blockchain..."})
        else:
            return jsonify ({"success": False, "reason": "User does not have permission to peform this action!"})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})

#protected with login_required decorator function
@account_bp.route('/get-user-events', methods=['GET'])
@login_required
def get_user_events():
    try:
        username_logs_requested = request.args.get('username')  # Retrieve the username from query parameters
    except:
        print("No username sent. Assuming session user logs will be sent.")
        username_logs_requested = None

    try:
        has_read_all = check_if_user_has_permission(session["username"], ["FaceGuard Read: All"])
        has_read_users = check_if_user_has_permission(session["username"], ["FaceGuard Read: Users"])
        has_read_self = check_if_user_has_permission(session["username"], ["FaceGuard Read: Self"])

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
            contract.events.User_UserAddedToGroup,
            contract.events.User_UserRemovedFromGroup
        ]

        #we will format the logs to return them to the FaceGuard app
        all_formatted_logs = []

        for event in events:
            event_logs = get_web3_event_logs_from_topic(event, username)

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
                        log_old_faceHashes = log["args"]["oldFaceHashes"]
                        log_new_faceHashes = log["args"]["newFaceHashes"]
                        event_data += f"uploaded new face hashes successfully ({log_old_faceHashes} => {log_new_faceHashes})."
                    case "UserEmailUpdated":
                        log_old_email = log["args"]["oldEmail"]
                        if log_old_email == "":
                            log_old_email = "' '"
                        log_new_email = log["args"]["newEmail"]
                        event_data += f"updated email address successfully ({log_old_email} => {log_new_email})."
                    case "UserFullNameUpdated":
                        log_old_full_name = log["args"]["oldFullName"]
                        if log_old_full_name == "":
                            log_old_full_name = "' '"
                        log_new_full_name = log["args"]["newFullName"]
                        event_data += f"updated full name successfully ({log_old_full_name} => {log_new_full_name})."
                    case "UserToggled":
                        log_enabled = log["args"]["enabled"]
                        if log_enabled:
                            event_data += "account has been enabled."
                        else:
                            event_data += "account has been disabled."
                    case "User_UserAddedToGroup":
                        log_group_name = log["args"]["groupName"]
                        event_data += f"added to permissions group successfully ({log_group_name})."
                    case "User_UserRemovedFromGroup":
                        log_group_name = log["args"]["groupName"]
                        event_data += f"removed from permissions group successfully ({log_group_name})."
                    case _:
                        event_data += "[Server Error: Event Not Implemented.]"
                
                all_formatted_logs.append({"timestamp": formatted_timestamp, "block": block_number, "event": event_name, "data": event_data})            

        all_formatted_logs.sort(key=lambda log: log["timestamp"], reverse=True)

        return jsonify ({"success": True, "reason": "Obtained user events successfully.", "logs": all_formatted_logs})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})

#protected with login_required decorator function
@account_bp.route('/get-group-events', methods=['GET'])
@login_required
def get_group_events():
    try:
        groupname_logs_requested = request.args.get('groupName')  # Retrieve the group name from query parameters
    except:
        print("No group name sent...")
        return jsonify ({"success": False, "reason": "No group name was sent with this request!"})
    
    try:
        has_read_all = check_if_user_has_permission(session["username"], "FaceGuard Read: All")
        has_read_groups = check_if_user_has_permission(session["username"], "FaceGuard Read: Groups")

        return_allowed = False

        if has_read_all or has_read_groups:
            return_allowed = True
        else:
            return_allowed = False

        if(return_allowed == False):
            return jsonify ({"success": False, "reason": "User does not have permission to perform this action!"})

        #list events to check for on the blockchain
        events = [
            contract.events.GroupCreated,
            contract.events.GroupPermissionsUpdated,
            contract.events.GroupNameUpdated,
            contract.events.GroupRemoved,
            contract.events.Group_UserAddedToGroup,
            contract.events.Group_UserRemovedFromGroup,
            contract.events.GroupAccessURLChanged
        ]

        #we will format the logs to return them to the FaceGuard app
        all_formatted_logs = []

        for event in events:
            event_logs = get_web3_event_logs_from_topic(event, groupname_logs_requested)

            for log in event_logs:
                block_number = int(log["blockNumber"])
                block_timestamp = w3.eth.get_block(block_number).timestamp
                formatted_timestamp = datetime.datetime.fromtimestamp(block_timestamp)

                event_name = log["event"]
                event_data = f"Group [{groupname_logs_requested}] "
                match event_name:
                    case "GroupCreated":
                        event_data += "was successfully created."
                    case "GroupPermissionsUpdated":
                        log_old_permissions_set = log["args"]["oldPermissions"]
                        log_new_permissions_set = log["args"]["newPermissions"]
                        event_data += f"has obtained new permission set successfully ({log_old_permissions_set} => {log_new_permissions_set})."
                    case "GroupNameUpdated":
                        log_old_name = log["args"]["oldGroupName"]
                        log_new_name = log["args"]["newGroupName"]
                        event_data += f"has obtained new name successfully ('{log_old_name}' => '{log_new_name}')."
                    case "GroupRemoved":
                        event_data += "has been deleted successfully."
                    case "GroupAccessURLChanged":
                        log_old_url = log["args"]["oldAccessURL"]
                        log_new_url = log["args"]["newAccessURL"]
                        event_data += f"changed access URL successfully ('{log_old_url}' => ''{log_new_url})."
                    case "Group_UserAddedToGroup":
                        log_username = log["args"]["username"]
                        event_data += f"added user successfully ({log_username})."
                    case "Group_UserRemovedFromGroup":
                        log_username = log["args"]["username"]
                        event_data += f"removed user successfully ({log_username})."
                    case _:
                        event_data += "[Server Error: Event Not Implemented.]"
                
                all_formatted_logs.append({"timestamp": formatted_timestamp, "block": block_number, "event": event_name, "data": event_data})            

        all_formatted_logs.sort(key=lambda log: log["timestamp"], reverse=True)

        return jsonify ({"success": True, "reason": "Obtained user events successfully.", "logs": all_formatted_logs})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})

#protected with login_required decorator function
@account_bp.route('/delete-self', methods=['GET'])
@login_required
def delete_self():
    try:
        has_delete_perm = check_if_user_has_permission(session["username"], ["FaceGuard Delete: All", "FaceGuard Delete: Users", "FaceGuard Delete: Self"])

        if has_delete_perm:
            print("User will be deleted...")
            transaction = write_to_blockchain(contract.functions.removeUser, [session["username"]])

            # Wait for confirmation of transaction
            receipt = w3.eth.wait_for_transaction_receipt(transaction)

            # Print transaction status
            if receipt.status == 1:
                return jsonify ({"success": True, "reason": "User deleted successfully."})
            else:
                return jsonify ({"success": False, "reason": "An error occurred while writing to the blockchain..."})
    except Exception as e:
        return jsonify ({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})