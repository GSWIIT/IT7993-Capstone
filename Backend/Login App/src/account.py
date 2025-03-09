from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from web3 import Web3
import os
import json
from login import login_required
from functools import wraps
from blockchain_connection import get_contract, get_w3_object, get_owner_address, get_private_key
import time

account_bp = Blueprint('permissions', __name__, template_folder='templates')

contract = get_contract()
w3 = get_w3_object()
owner_address = get_owner_address()
PRIVATE_KEY = get_private_key()

#protected with login_required decorator function
@account_bp.route('/get-users', methods=['GET'])
@login_required
def get_all_users():
    #get user permissions first
    permissions = contract.functions.getUserPermissions(session["username"]).call()
def save_name():
    data = request.get_json()
    username = session.get("username")
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    if not first_name or not last_name:
        return jsonify({"success": False, "reason": "First name and last name are required."})

    # Save the names to the blockchain
    try:
        tx = contract.functions.updateUserName(first_name, last_name).build_transaction({
            "from": owner_address,
            "nonce": w3.eth.get_transaction_count(owner_address),
            "gas": 200000,  # Adjust gas limit as needed
            "gasPrice": w3.eth.gas_price,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            return jsonify({"success": True, "reason": "Names saved successfully."})
        else:
            return jsonify({"success": False, "reason": "Transaction failed."})
    except Exception as e:
        return jsonify({"success": False, "reason": str(e)})