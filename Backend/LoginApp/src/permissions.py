from flask import Blueprint, request, session, jsonify
from login import login_required
from blockchain_connection import get_contract, get_w3_object, write_to_blockchain
from bs4 import BeautifulSoup
import requests

permissions_bp = Blueprint('permissions', __name__, template_folder='templates')

contract = get_contract()
w3 = get_w3_object()

def check_if_user_has_permission(username, permissionsList):
    try:
        #get user permissions first
        permissions = contract.functions.getUserPermissions(username).call()

        has_permission = False
        for listedPermission in permissionsList:
            permissionFound = any(listedPermission in perm for perm in permissions)
            if permissionFound:
                has_permission = True
                break

        return has_permission
    except Exception as e:
        raise Exception("Internal server error: " + str(e.args[0]) + "!")
    
def consolidate_core_permissions(permissions):
    hierarchy = {
            "Self": 1,
            "Groups": 2,
            "Users": 3,
            "All": 4
        }
    
    consolidated_permissions = []
    permission_map = {}

    permission_list = []
    for perm in permissions:
        if 'FaceGuard' in perm:
            permission_list.append(perm)
        else:
            consolidated_permissions.append(perm)

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
    for category, levels in permission_map.items():
        if "All" in levels:  
            # "All" overrides everything else, so just keep it
            consolidated_permissions.append(f"{category}: All")
        else:
            # Keep multiple scopes (e.g., both "Group" and "Users" if present)
            sorted_levels = sorted(levels, key=lambda lvl: hierarchy[lvl])  # Sort by hierarchy
            consolidated_permissions.append(f"{category}: {', '.join(sorted_levels)}")

    return consolidated_permissions

def get_page_title(url):
    response = requests.get(url, timeout=10)
    if(response.status_code != 200):
        raise Exception("Bad response.")
    
    response.raise_for_status()  # Raise an error for bad status codes
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string.strip()
    return title

#protected with login_required decorator function
@permissions_bp.route('/get-users', methods=['GET'])
@login_required
def get_all_users():
    try:
        has_read_all_users = check_if_user_has_permission(session["username"], ["FaceGuard Read: All"])
        has_read_users_manager = check_if_user_has_permission(session["username"], ["FaceGuard Read: Users"])
        has_read_self_only = check_if_user_has_permission(session["username"], ["FaceGuard Read: Self"])

        all_users_array = []

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
                    "enabled": user[5],
                    "fullName": user[6],
                    "email": user[7]
                })

        return jsonify({"success": True, "reason": "Users returned successfully based on permissions.", "array": all_users_array})
    except Exception as e:
        return jsonify({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})

#protected with login_required decorator function
@permissions_bp.route('/get-all-quick-url-links', methods=['GET'])
@login_required
def get_all_quick_url_links():
    try:
        has_read_self_group_only = check_if_user_has_permission(session["username"], ["FaceGuard Read: Self"])

        all_quick_links_array = []

        print("User [" + str(session["username"]) + "] has permission to read self: ", has_read_self_group_only)

        groupNames = contract.functions.getAllGroups().call()

        if has_read_self_group_only:
            for group in groupNames:
                group_obj = contract.functions.getGroup(group).call()
                include_in_return_array = False

                session_user_found_in_group = session["username"] in group_obj[2]

                if session_user_found_in_group:
                    include_in_return_array = True

                if include_in_return_array:
                    if(group_obj[3] != ""):
                        page_title = ""
                        page_url = group_obj[3]

                        try:
                            page_title = get_page_title(group_obj[3])
                        except:
                            page_title = page_url

                        all_quick_links_array.append([page_title, page_url])

            if all_quick_links_array.count == 0:
                return jsonify({"success": False, "reason": "Request completed successfully, but there were no URLs found.", "array": None})
            else:
                return jsonify({"success": True, "reason": "URLs obtained successfully.", "array": all_quick_links_array})
        else:
            jsonify({"success": False, "reason": "User does not have permission to view any groups!", "array": None})
    except Exception as e:
        return jsonify({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})

#protected with login_required decorator function
@permissions_bp.route('/get-groups', methods=['GET'])
@login_required
def get_all_groups():
    try:
        has_read_all_groups = check_if_user_has_permission(session["username"], ["FaceGuard Read: All"])
        has_read_groups_manager = check_if_user_has_permission(session["username"], ["FaceGuard Read: Groups"])
        has_read_self_group_only = check_if_user_has_permission(session["username"], ["FaceGuard Read: Self"])

        all_groups_array = []

        print("User [" + str(session["username"]) + "] has permission to read all groups: ", (has_read_all_groups or has_read_groups_manager))
        print("User [" + str(session["username"]) + "] has permission to read self groups only: ", has_read_self_group_only)

        groupNames = contract.functions.getAllGroups().call()

        #if user does not have the "Read All Groups" permission, not all groups will return
        #all_groups_array will change based on what permissions are present!

        for group in groupNames:
            group_obj = contract.functions.getGroup(group).call()
            include_in_return_array = False

            if (has_read_all_groups or has_read_groups_manager):
                include_in_return_array = True
            else:
                if has_read_self_group_only:
                    session_user_found_in_group = session["username"] in group_obj[2]

                    if session_user_found_in_group:
                        include_in_return_array = True

            if include_in_return_array:
                all_groups_array.append({
                    "name": group_obj[0], 
                    "permissions": group_obj[1],
                    "members": group_obj[2],
                    "url": group_obj[3]
                })

        if all_groups_array.count == 0:
            return jsonify({"success": False, "reason": "User does not have permission to view any groups!", "array": None})
        else:
            return jsonify({"success": True, "reason": "Groups found successfully based on user permissions.", "array": all_groups_array})
    except Exception as e:
        return jsonify({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})

#protected with login_required decorator function
@permissions_bp.route('/get-user-permissions', methods=['GET'])
@login_required
def get_user_permissions():
    try:
        permissions = contract.functions.getUserPermissions(session["username"]).call()

        print("User [" + str(session["username"]) + "] permissions: ", permissions)

        permissions = consolidate_core_permissions(permissions)

        return jsonify({"success": True, "reason": "Permissions obtained successfully.", "array": permissions})
    except Exception as e:
        return jsonify({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})

#protected with login_required decorator function
@permissions_bp.route('/create-group', methods=['POST'])
@login_required
def create_group():
    try:
        data = request.get_json()
        groupName = data.get("groupName")
        groupPermissions = data.get("groupPermissions")
        groupURL = data.get("groupURL")

        has_create_group_permissions = check_if_user_has_permission(session["username"], ["FaceGuard Create: All", "FaceGuard Create: Groups"])

        print("User [" + str(session["username"]) + "] has permission to create groups: ", has_create_group_permissions)

        if has_create_group_permissions:
            print("Estimating gas...")
            transaction = write_to_blockchain(contract.functions.createGroup, [groupName, groupPermissions, groupURL])

            # Wait for confirmation of transaction
            receipt = w3.eth.wait_for_transaction_receipt(transaction)

            # Print transaction status
            if receipt.status == 1:
                return jsonify({"success": True, "reason": "Group created successfully."})
            else:
                return jsonify({"success": False, "reason": "Error encountered while writing to the blockchain..."})
        else:
            return jsonify({"success": False, "reason": "User does not have permission to perform this action!"})
    except Exception as e:
        return jsonify({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})
    
#protected with login_required decorator function
@permissions_bp.route('/update-group', methods=['POST'])
@login_required
def update_group():
    try:
        data = request.get_json()
        originalGroupName = data.get("originalGroupName")
        newGroupName = data.get("newGroupName")
        groupPermissions = data.get("groupPermissions")

        has_update_group_permissions = check_if_user_has_permission(session["username"], ["FaceGuard Update: All", "FaceGuard Update: Groups"])
        print("User [" + str(session["username"]) + "] has permission to update groups: ", has_update_group_permissions)

        if has_update_group_permissions:
            #estimate the cost of the ethereum transaction by predicting gas
            transaction = write_to_blockchain(contract.functions.updateGroup, [originalGroupName, newGroupName, groupPermissions])

            # Wait for confirmation of transaction
            receipt = w3.eth.wait_for_transaction_receipt(transaction)

            # Print transaction status
            if receipt.status == 1:
                print("Updated group name successfully.", "Group permissions updated successfully.")
                return jsonify({"success": True, "reason": "Group permissions updated successfully."})
            else:
                return jsonify({"success": False, "reason": "Error encountered while writing to the blockchain..."})
        else:
            return jsonify({"success": False, "reason": "User does not have permission to perform this action!"})
    except Exception as e:
        return jsonify({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})
    
    #protected with login_required decorator function
@permissions_bp.route('/update-group-access-url', methods=['POST'])
@login_required
def update_group_access_url():
    try:
        data = request.get_json()
        groupName = data.get("groupName")
        groupURL = data.get("accessURL")

        has_update_group_permissions = check_if_user_has_permission(session["username"], ["FaceGuard Update: All", "FaceGuard Update: Groups"])
        print("User [" + str(session["username"]) + "] has permission to update groups: ", has_update_group_permissions)

        if has_update_group_permissions:
            #estimate the cost of the ethereum transaction by predicting gas
            transaction = write_to_blockchain(contract.functions.setGroupURL, [groupName, groupURL])

            # Wait for confirmation of transaction
            receipt = w3.eth.wait_for_transaction_receipt(transaction)

            # Print transaction status
            if receipt.status == 1:
                print("Updated group name successfully.", "Group permissions updated successfully.")
                return jsonify({"success": True, "reason": "Group permissions updated successfully."})
            else:
                return jsonify({"success": False, "reason": "Error encountered while writing to the blockchain..."})
        else:
            return jsonify({"success": False, "reason": "User does not have permission to perform this action!"})
    except Exception as e:
        return jsonify({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})
    
#protected with login_required decorator function
@permissions_bp.route('/add-group-user', methods=['POST'])
@login_required
def add_user_to_group():
    try:
        data = request.get_json()
        groupName = data.get("groupName")
        usernameToUpdate = data.get("username")

        has_update_group_permissions = check_if_user_has_permission(session["username"], ["FaceGuard Update: All", "FaceGuard Update: Groups"])
        print("User [" + str(session["username"]) + "] has permission to update groups: ", has_update_group_permissions)

        if has_update_group_permissions:
            transaction = write_to_blockchain(contract.functions.addUserToGroup, [groupName, usernameToUpdate])

            # Wait for confirmation of transaction
            receipt = w3.eth.wait_for_transaction_receipt(transaction)

            # Print transaction status
            if receipt.status == 1:
                print("Updated group name successfully.")
                print("Group permissions updated successfully.")
                return jsonify({"success": True, "reason": "Group permissions updated successfully."})
            else:
                return jsonify({"success": False, "reason": "Error encountered while writing to the blockchain..."})
        else:
            return jsonify({"success": False, "reason": "User does not have permission to perform this action!"})
    except Exception as e:
        return jsonify({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})
    
#protected with login_required decorator function
@permissions_bp.route('/remove-group-user', methods=['POST'])
@login_required
def remove_user_to_group():
    try:
        data = request.get_json()
        groupName = data.get("groupName")
        usernameToUpdate = data.get("username")

        has_update_group_permissions = check_if_user_has_permission(session["username"], ["FaceGuard Update: All", "FaceGuard Update: Groups"])
        print("User [" + str(session["username"]) + "] has permission to update groups: ", has_update_group_permissions)

        if has_update_group_permissions:
            transaction = write_to_blockchain(contract.functions.removeUserFromGroup, [groupName, usernameToUpdate])

            # Wait for confirmation of transaction
            receipt = w3.eth.wait_for_transaction_receipt(transaction)

            # Print transaction status
            if receipt.status == 1:
                print("Updated group name successfully.")
                print("Group permissions updated successfully.")
                return jsonify({"success": True, "reason": "Group permissions updated successfully."})
            else:
                return jsonify({"success": False, "reason": "Error encountered while writing to the blockchain..."})
        else:
            return jsonify({"success": False, "reason": "User does not have permission to perform this action!"})
    except Exception as e:
        return jsonify({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})
    
#protected with login_required decorator function
@permissions_bp.route('/delete-group', methods=['POST'])
@login_required
def delete_group():
    try:
        data = request.get_json()
        groupName = data.get("groupName")

        has_delete_group_permission = check_if_user_has_permission(session["username"], ["FaceGuard Delete: All"])
        has_delete_group_manager_permission = check_if_user_has_permission(session["username"], ["FaceGuard Delete: Groups"])
        print("User [" + str(session["username"]) + "] has permission to update groups: ", (has_delete_group_permission) or (has_delete_group_manager_permission))

        if (has_delete_group_permission) or (has_delete_group_manager_permission):
            transaction = write_to_blockchain(contract.functions.removeGroup, [groupName])

            # Wait for confirmation of transaction
            receipt = w3.eth.wait_for_transaction_receipt(transaction)

            # Print transaction status
            if receipt.status == 1:
                print("Deleted group successfully.")
                return jsonify({"success": True, "reason": "Deleted group successfully."})
            else:
                return jsonify({"success": False, "reason": "Error encountered while writing to the blockchain..."})
        else:
            return jsonify({"success": False, "reason": "User does not have permission to perform this action!"})
    except Exception as e:
        return jsonify({"success": False, "reason": "Internal server error: " + str(e.args[0]) + "!"})