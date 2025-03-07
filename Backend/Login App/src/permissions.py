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
    has_read_all_users = "Read All Users" in permissions
    has_read_self_only = "Read Self Only" in permissions

    #if user does not have the "Read All Users" permission, not all users will be returned!
    #all_users_array will change based on the session user's permissions!

    usernames = contract.functions.getAllUsernames().call()

    for username in usernames:
        include_in_return_array = False

        if has_read_all_users:
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
                "enabled": user[6]
            })

    return jsonify({"success": True, "reason": "Users returned successfully based on permissions.", "array": all_users_array})


#protected with login_required decorator function
@permissions_bp.route('/get-groups', methods=['GET'])
@login_required
def get_all_groups():
    #get user permissions first
    permissions = contract.functions.getUserPermissions(session["username"]).call()

    all_groups_array = []
    has_read_all_groups = "Read All Groups" in permissions
    has_read_self_group_only = "Read Self Groups Only" in permissions

    print("User [" + str(session["username"]) + "] has permission to read all groups: ", has_read_all_groups)
    print("User [" + str(session["username"]) + "] has permission to read self groups only: ", has_read_self_group_only)

    groupNames = contract.functions.getAllGroups().call()

    #if user does not have the "Read All Groups" permission, not all groups will return
    #all_groups_array will change based on what permissions are present!

    for group in groupNames:
        group_obj = contract.functions.getGroup(group).call()
        include_in_return_array = False

        if has_read_all_groups:
            include_in_return_array = True
        else:
            if has_read_self_group_only:
                print(session["username"], group_obj[2])
                print(session["username"] in group_obj[2])
                session_user_found_in_group = session["username"] in group_obj[2]

                if session_user_found_in_group:
                    include_in_return_array = True

        if include_in_return_array:
            all_groups_array.append({
                "name": group_obj[0], 
                "members": group_obj[2],
                "permissions": group_obj[1]
            })

    print(all_groups_array)

    if all_groups_array.count == 0:
        return jsonify({"success": False, "reason": "User does not have permission to view any groups!", "array": None})
    else:
        return jsonify({"success": True, "reason": "Groups found successfully based on user permissions.", "array": all_groups_array})

#protected with login_required decorator function
@permissions_bp.route('/get-user-permissions', methods=['GET'])
@login_required
def get_user_permissions():
    permissions = contract.functions.getUserPermissions(session["username"]).call()

    print("User [" + str(session["username"]) + "] permissions: ", permissions)

    return jsonify({"success": True, "reason": "Permissions obtained successfully.", "array": permissions})

#protected with login_required decorator function
@permissions_bp.route('/create-group', methods=['POST'])
@login_required
def create_group():
    data = request.get_json()
    groupName = data.get("groupName")
    groupPermissions = data.get("groupPermissions")

    permissions = contract.functions.getUserPermissions(session["username"]).call()

    print("User [" + str(session["username"]) + "] permissions: ", permissions)
    has_create_all = "Create All" in permissions
    print("User [" + str(session["username"]) + "] has permission to create all: ", has_create_all)

    if has_create_all:
        print("Estimating gas...")
        #estimate the cost of the ethereum transaction by predicting gas
        estimated_gas = contract.functions.createGroup(groupName).estimate_gas({"from": owner_address})

        # Get the suggested gas price
        gas_price = w3.eth.gas_price  # Fetch the current network gas price dynamically
        max_priority_fee = w3.to_wei("2", "gwei")  # Priority fee (adjust based on congestion)
        max_fee_per_gas = gas_price + max_priority_fee

        tx = contract.functions.createGroup(groupName).build_transaction({
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
            print(f"Group creation transaction successful! Block: {receipt.blockNumber}")
            time.sleep(5)

            estimated_gas = contract.functions.setGroupPermissions(groupName, groupPermissions).estimate_gas({"from": owner_address})

            # Get the suggested gas price
            gas_price = w3.eth.gas_price  # Fetch the current network gas price dynamically
            max_priority_fee = w3.to_wei("2", "gwei")  # Priority fee (adjust based on congestion)
            max_fee_per_gas = gas_price + max_priority_fee

            tx = contract.functions.setGroupPermissions(groupName, groupPermissions).build_transaction({
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

            if receipt.status == 1:
                return jsonify({"success": True, "reason": "Group created successfully."})
            else:
                return jsonify({"success": False, "reason": "Error encountered while writing to the blockchain..."})
    else:
        return jsonify({"success": False, "reason": "User does not have permission to perform this action!"})