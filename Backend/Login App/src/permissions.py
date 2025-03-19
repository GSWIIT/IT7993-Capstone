from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from web3 import Web3
import os
import json
from login import login_required
from functools import wraps
from blockchain_connection import get_contract, get_w3_object, get_owner_address, get_private_key
import time

permissions_bp = Blueprint('permissions', __name__, template_folder='templates')

contract = get_contract()
w3 = get_w3_object()
owner_address = get_owner_address()
PRIVATE_KEY = get_private_key()

#protected with login_required decorator function
@permissions_bp.route('/get-users', methods=['GET'])
@login_required
def get_all_users():
    #get user permissions first
    permissions = contract.functions.getUserPermissions(session["username"]).call()

    all_users_array = []
    has_read_all_users = any("FaceGuard Read: All" in perm for perm in permissions)
    has_read_users_manager = any("FaceGuard Read: Users" in perm for perm in permissions)
    has_read_self_only = any("FaceGuard Read: Self" in perm for perm in permissions)

    #if user does not have permission, not all users will be returned!
    #all_users_array will change based on the session user's permissions!

    usernames = contract.functions.getAllUsernames().call()

    for username in usernames:
        include_in_return_array = False

        if (has_read_all_users) or (has_read_users_manager):
            include_in_return_array = True
        else:
            if has_read_self_only:
                if session["username"] == username:
                    include_in_return_array = True

        if include_in_return_array:
            user = contract.functions.getUser(username).call()
            face_hashes_exist = False

            if user[2] is not None:
                face_hashes_exist = True

            all_users_array.append({
                "username": user[0], 
                "faceHashes": face_hashes_exist,
                "accountCreationDate": user[3],
                "lastEditDate": user[4],
                "faceReenrollmentRequired": user[5],
                "enabled": user[6],
                "fullName": user[7],
                "email": user[8]
            })

    return jsonify({"success": True, "reason": "Users returned successfully based on permissions.", "array": all_users_array})


#protected with login_required decorator function
@permissions_bp.route('/get-groups', methods=['GET'])
@login_required
def get_all_groups():
    #get user permissions first
    permissions = contract.functions.getUserPermissions(session["username"]).call()

    all_groups_array = []
    has_read_all_groups = any("FaceGuard Read: All" in perm for perm in permissions)
    has_read_groups_manager = any("FaceGuard Read: Groups" in perm for perm in permissions)
    has_read_self_group_only = any("FaceGuard Read: Self" in perm for perm in permissions)

    print("User [" + str(session["username"]) + "] has permission to read all groups: ", has_read_all_groups)
    print("User [" + str(session["username"]) + "] has permission to read self groups only: ", has_read_self_group_only)

    groupNames = contract.functions.getAllGroups().call()

    #if user does not have the "Read All Groups" permission, not all groups will return
    #all_groups_array will change based on what permissions are present!

    for group in groupNames:
        group_obj = contract.functions.getGroup(group).call()
        include_in_return_array = False

        if (has_read_all_groups) or (has_read_groups_manager):
            include_in_return_array = True
        else:
            if has_read_self_group_only:
                session_user_found_in_group = session["username"] in group_obj[2]

                if session_user_found_in_group:
                    include_in_return_array = True

        if include_in_return_array:
            all_groups_array.append({
                "name": group_obj[0], 
                "members": group_obj[2],
                "permissions": group_obj[1]
            })

    if all_groups_array.count == 0:
        return jsonify({"success": False, "reason": "User does not have permission to view any groups!", "array": None})
    else:
        return jsonify({"success": True, "reason": "Groups found successfully based on user permissions.", "array": all_groups_array})

def consolidate_core_permissions(permission_list):
    hierarchy = {
            "Self": 1,
            "Group": 2,
            "Users": 3,
            "All": 4
        }
    
    permission_map = {}

    for perm in permission_list:
        parts = perm.split(": ")
        if len(parts) == 2:
            category, level = parts
            level = level.strip()
            
            # Ensure the category has a set to store all relevant scopes
            if category not in permission_map:
                permission_map[category] = set()
            
            permission_map[category].add(level)

    # Consolidate permissions while keeping multiple scopes if necessary
    consolidated_permissions = []
    for category, levels in permission_map.items():
        if "All" in levels:  
            # "All" overrides everything else, so just keep it
            consolidated_permissions.append(f"{category}: All")
        else:
            # Keep multiple scopes (e.g., both "Group" and "Users" if present)
            sorted_levels = sorted(levels, key=lambda lvl: hierarchy[lvl])  # Sort by hierarchy
            consolidated_permissions.append(f"{category}: {', '.join(sorted_levels)}")

    return consolidated_permissions

#protected with login_required decorator function
@permissions_bp.route('/get-user-permissions', methods=['GET'])
@login_required
def get_user_permissions():
    permissions = contract.functions.getUserPermissions(session["username"]).call()

    print("User [" + str(session["username"]) + "] permissions: ", permissions)

    permissions = consolidate_core_permissions(permissions)

    return jsonify({"success": True, "reason": "Permissions obtained successfully.", "array": permissions})

#protected with login_required decorator function
@permissions_bp.route('/routed-system-access', methods=['GET'])
@login_required
def verify_user_route_access():

    permissions = get_user_permissions()

    has_access_to_website = ("Website Access: Google" in permissions)

    if(has_access_to_website):
        return redirect("www.google.com")
    else:
        return jsonify ({"success": False})

#protected with login_required decorator function
@permissions_bp.route('/create-group', methods=['POST'])
@login_required
def create_group():
    data = request.get_json()
    groupName = data.get("groupName")
    groupPermissions = data.get("groupPermissions")

    permissions = contract.functions.getUserPermissions(session["username"]).call()

    print("User [" + str(session["username"]) + "] permissions: ", permissions)
    has_create_group_permissions = ("FaceGuard Create: All" in permissions) or ("FaceGuard Create: Groups" in permissions)
    print("User [" + str(session["username"]) + "] has permission to create groups: ", has_create_group_permissions)

    if has_create_group_permissions:
        print("Estimating gas...")
        #estimate the cost of the ethereum transaction by predicting gas
        estimated_gas = contract.functions.createGroup(groupName, groupPermissions).estimate_gas({"from": owner_address})

        # Get the suggested gas price
        gas_price = w3.eth.gas_price  # Fetch the current network gas price dynamically
        max_priority_fee = w3.to_wei("4", "gwei")  # Priority fee (adjust based on congestion)
        max_fee_per_gas = gas_price + max_priority_fee

        tx = contract.functions.createGroup(groupName, groupPermissions).build_transaction({
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
            return jsonify({"success": True, "reason": "Group created successfully."})
        else:
            return jsonify({"success": False, "reason": "Error encountered while writing to the blockchain..."})
    else:
        return jsonify({"success": False, "reason": "User does not have permission to perform this action!"})
    
#protected with login_required decorator function
@permissions_bp.route('/update-group', methods=['POST'])
@login_required
def update_group():
    data = request.get_json()
    originalGroupName = data.get("originalGroupName")
    newGroupName = data.get("newGroupName")
    groupPermissions = data.get("groupPermissions")

    print(originalGroupName, newGroupName, groupPermissions)

    permissions = contract.functions.getUserPermissions(session["username"]).call()

    print("User [" + str(session["username"]) + "] permissions: ", permissions)
    has_update_group_permissions = ("FaceGuard Update: All" in permissions) or ("FaceGuard Update: Groups" in permissions)
    print("User [" + str(session["username"]) + "] has permission to update groups: ", has_update_group_permissions)

    if has_update_group_permissions:
        print("Group needs update: ", originalGroupName != newGroupName)
        #estimate the cost of the ethereum transaction by predicting gas
        print("Estimating gas...")
        try:
            estimated_gas = contract.functions.updateGroup(originalGroupName, newGroupName, groupPermissions).estimate_gas({"from": owner_address})
        except Exception as e:
            return jsonify ({"success": False, "reason": "Error encountered! Blockchain Response[" + str(e.args[0]) + "]."})

        # Get the suggested gas price
        gas_price = w3.eth.gas_price  # Fetch the current network gas price dynamically
        max_priority_fee = w3.to_wei("4", "gwei")  # Priority fee (adjust based on congestion)
        max_fee_per_gas = gas_price + max_priority_fee

        tx = contract.functions.updateGroup(originalGroupName, newGroupName, groupPermissions).build_transaction({
            "from": owner_address,
            "nonce": w3.eth.get_transaction_count(owner_address),
            "gas": estimated_gas + 200000, 
            "maxFeePerGas": max_fee_per_gas,  # Total fee
            "maxPriorityFeePerGas": max_priority_fee,  # Tip for miners
        })

        # Sign transaction with private key
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)

        print("Sending group update transaction...")
        # Send transaction to blockchain
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Wait for confirmation of transaction
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        # Print transaction status
        if receipt.status == 1:
            print("Updated group name successfully.")
            print("Group permissions updated successfully.")
            return jsonify({"success": True, "reason": "Group permissions updated successfully."})
        else:
            return jsonify({"success": False, "reason": "Error encountered while writing to the blockchain..."})
    else:
        return jsonify({"success": False, "reason": "User does not have permission to perform this action!"})
    
#protected with login_required decorator function
@permissions_bp.route('/add-group-user', methods=['POST'])
@login_required
def add_user_to_group():
    data = request.get_json()
    groupName = data.get("groupName")
    usernameToUpdate = data.get("username")

    print(groupName, usernameToUpdate)

    permissions = contract.functions.getUserPermissions(session["username"]).call()

    print("User [" + str(session["username"]) + "] permissions: ", permissions)
    has_update_group_permissions = ("FaceGuard Update: All" in permissions) or ("FaceGuard Update: Groups" in permissions)
    print("User [" + str(session["username"]) + "] has permission to update groups: ", has_update_group_permissions)

    if has_update_group_permissions:
        #estimate the cost of the ethereum transaction by predicting gas
        print("Estimating gas...")
        estimated_gas = contract.functions.addUserToGroup(groupName, usernameToUpdate).estimate_gas({"from": owner_address})

        # Get the suggested gas price
        gas_price = w3.eth.gas_price  # Fetch the current network gas price dynamically
        max_priority_fee = w3.to_wei("4", "gwei")  # Priority fee (adjust based on congestion)
        max_fee_per_gas = gas_price + max_priority_fee

        tx = contract.functions.addUserToGroup(groupName, usernameToUpdate).build_transaction({
            "from": owner_address,
            "nonce": w3.eth.get_transaction_count(owner_address),
            "gas": estimated_gas + 200000, 
            "maxFeePerGas": max_fee_per_gas,  # Total fee
            "maxPriorityFeePerGas": max_priority_fee,  # Tip for miners
        })

        # Sign transaction with private key
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)

        print("Sending transaction to add user to group...")
        # Send transaction to blockchain
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Wait for confirmation of transaction
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        # Print transaction status
        if receipt.status == 1:
            print("Updated group name successfully.")
            print("Group permissions updated successfully.")
            return jsonify({"success": True, "reason": "Group permissions updated successfully."})
        else:
            return jsonify({"success": False, "reason": "Error encountered while writing to the blockchain..."})
    else:
        return jsonify({"success": False, "reason": "User does not have permission to perform this action!"})
    
#protected with login_required decorator function
@permissions_bp.route('/remove-group-user', methods=['POST'])
@login_required
def remove_user_to_group():
    data = request.get_json()
    groupName = data.get("groupName")
    usernameToUpdate = data.get("username")

    print(groupName, usernameToUpdate)

    permissions = contract.functions.getUserPermissions(session["username"]).call()

    print("User [" + str(session["username"]) + "] permissions: ", permissions)
    has_update_group_permissions = ("FaceGuard Update: All" in permissions) or ("FaceGuard Update: Groups" in permissions)
    print("User [" + str(session["username"]) + "] has permission to update groups: ", has_update_group_permissions)

    if has_update_group_permissions:
        #estimate the cost of the ethereum transaction by predicting gas
        print("Estimating gas...")
        estimated_gas = contract.functions.removeUserFromGroup(groupName, usernameToUpdate).estimate_gas({"from": owner_address})

        # Get the suggested gas price
        gas_price = w3.eth.gas_price  # Fetch the current network gas price dynamically
        max_priority_fee = w3.to_wei("4", "gwei")  # Priority fee (adjust based on congestion)
        max_fee_per_gas = gas_price + max_priority_fee

        tx = contract.functions.removeUserFromGroup(groupName, usernameToUpdate).build_transaction({
            "from": owner_address,
            "nonce": w3.eth.get_transaction_count(owner_address),
            "gas": estimated_gas + 200000, 
            "maxFeePerGas": max_fee_per_gas,  # Total fee
            "maxPriorityFeePerGas": max_priority_fee,  # Tip for miners
        })

        # Sign transaction with private key
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)

        print("Sending transaction to remove user from group...")
        # Send transaction to blockchain
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Wait for confirmation of transaction
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        # Print transaction status
        if receipt.status == 1:
            print("Updated group name successfully.")
            print("Group permissions updated successfully.")
            return jsonify({"success": True, "reason": "Group permissions updated successfully."})
        else:
            return jsonify({"success": False, "reason": "Error encountered while writing to the blockchain..."})
    else:
        return jsonify({"success": False, "reason": "User does not have permission to perform this action!"})
    
#protected with login_required decorator function
@permissions_bp.route('/delete-group', methods=['POST'])
@login_required
def delete_group():
    data = request.get_json()
    groupName = data.get("groupName")

    permissions = contract.functions.getUserPermissions(session["username"]).call()

    print("User [" + str(session["username"]) + "] permissions: ", permissions)
    has_delete_group_permission = any("FaceGuard Delete: All" in perm for perm in permissions)
    has_delete_group_manager_permission = any("FaceGuard Delete: Groups" in perm for perm in permissions)
    print("User [" + str(session["username"]) + "] has permission to update groups: ", (has_delete_group_permission) or (has_delete_group_manager_permission))

    if (has_delete_group_permission) or (has_delete_group_manager_permission):
        #estimate the cost of the ethereum transaction by predicting gas
        print("Estimating gas...")
        try:
            estimated_gas = contract.functions.removeGroup(groupName).estimate_gas({"from": owner_address})
        except Exception as e:
            return jsonify ({"success": False, "reason": "Blockchain exception caught! Error:" + str(e.args[0]) + "!"})

        # Get the suggested gas price
        gas_price = w3.eth.gas_price  # Fetch the current network gas price dynamically
        max_priority_fee = w3.to_wei("4", "gwei")  # Priority fee (adjust based on congestion)
        max_fee_per_gas = gas_price + max_priority_fee

        tx = contract.functions.removeGroup(groupName).build_transaction({
            "from": owner_address,
            "nonce": w3.eth.get_transaction_count(owner_address),
            "gas": estimated_gas + 200000, 
            "maxFeePerGas": max_fee_per_gas,  # Total fee
            "maxPriorityFeePerGas": max_priority_fee,  # Tip for miners
        })

        # Sign transaction with private key
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)

        print("Sending transaction to delete group...")
        # Send transaction to blockchain
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Wait for confirmation of transaction
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        # Print transaction status
        if receipt.status == 1:
            print("Deleted group successfully.")
            return jsonify({"success": True, "reason": "Deleted group successfully."})
        else:
            return jsonify({"success": False, "reason": "Error encountered while writing to the blockchain..."})
    else:
        return jsonify({"success": False, "reason": "User does not have permission to perform this action!"})
    