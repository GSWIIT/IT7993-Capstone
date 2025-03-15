// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FaceGuard {
    struct User {
        string username;
        string passwordHash;
        string[] faceHashes;
        string accountCreationDate;
        string lastEditDate;
        bool faceReenrollmentRequired;
        bool passwordChangeRequired;
        bool enabled;
        string email;
        string fullName;
    }

    struct Group {
        string name;
        string[] members;
        string[] permissions;
    }

    mapping(string => User) private users;
    mapping(string => Group) private groups;
    string[] private allUsernames; // Array to store all created users
    string[] private allGroupNames; //Array to store group names, so they can be called later

    address private owner;

    event UserRegistered(string indexed username);
    event UserLoggedIn(string indexed username);
    event PasswordUpdated(string indexed username);
    event PasswordChangeRequired(string indexed username);
    event FaceHashUpdated(string indexed username);
    event UserEmailUpdated(string indexed username, string oldEmail, string newEmail);
    event UserFullNameUpdated(string indexed username, string oldFullName, string newFullName);
    event UserToggled(string indexed username, bool enabled);
    event GroupCreated(string indexed groupName, string[] permissions);
    event UserAddedToGroup(string indexed username, string groupName);
    event UserRemovedFromGroup(string indexed username, string groupName);
    event GroupPermissionsUpdated(string indexed groupName, string[] permissions);
    event GroupNameUpdated(string indexed originalGroupName, string newGroupName);
    event GroupRemoved(string indexed groupName);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the contract owner can perform this action");
        _;
    }

    constructor() {
        owner = msg.sender;

        // Define the core groups permissions
        string[4] memory adminPermissions = ["FaceGuard Create: All", "FaceGuard Read: All", "FaceGuard Update: All", "FaceGuard Delete: All"];
        string[3] memory userPermissions = ["FaceGuard Read: Self", "FaceGuard Update: Self", "FaceGuard Delete: Self"];
        string[4] memory groupManagersPermissions = ["FaceGuard Create: Groups", "FaceGuard Read: Groups", "FaceGuard Update: Groups", "FaceGuard Delete: Groups"];
        string[4] memory userManagersPermissions = ["FaceGuard Create: Users", "FaceGuard Read: Users", "FaceGuard Update: Users", "FaceGuard Delete: Users"];

        //create groups
        createGroup("Administrators", convertToDynamic(adminPermissions));
        createGroup("Users", convertToDynamic(userPermissions));
        createGroup("Group Managers", convertToDynamic(groupManagersPermissions));
        createGroup("User Managers", convertToDynamic(userManagersPermissions));
    }

    // Helper function to convert fixed-size array to dynamically-sized array
    function convertToDynamic(string[4] memory fixedArray) private pure returns (string[] memory) {
        string[] memory dynamicArray = new string[](fixedArray.length);
        for (uint i = 0; i < fixedArray.length; i++) {
            dynamicArray[i] = fixedArray[i];
        }
        return dynamicArray;
    }

    function convertToDynamic(string[3] memory fixedArray) private pure returns (string[] memory) {
        string[] memory dynamicArray = new string[](fixedArray.length);
        for (uint i = 0; i < fixedArray.length; i++) {
            dynamicArray[i] = fixedArray[i];
        }
        return dynamicArray;
    }

    function registerUser(string memory username, string memory passwordHash, string[] memory initialFaceHashes, string memory creationDate) public onlyOwner {
        users[username] = User(username, passwordHash, initialFaceHashes, creationDate, creationDate, false, false, true, "", "");
        allUsernames.push(username);
        addUserToGroup("Users", username);
        emit UserRegistered(username);

        //if this is the very first user in the smart contract, we will also add them to the administrators group.
        if (allUsernames.length == 1) {
            addUserToGroup("Administrators", username);
        }
    }

    function emitLoginSuccessLog(string memory username) public onlyOwner {
        emit UserLoggedIn(username);
    }

    function getUserFaceHashes(string memory username) public view returns (string[] memory) {
        return users[username].faceHashes;
    }

    function updateUserPassword(string memory username, string memory newPasswordHash) public onlyOwner {
        users[username].passwordHash = newPasswordHash;
        users[username].passwordChangeRequired = false;
        emit PasswordUpdated(username);
    }

    function updateUserFaceHash(string memory username, string[] memory newFaceHashes) public onlyOwner {
        users[username].faceHashes = newFaceHashes;
        emit FaceHashUpdated(username);
    }

    function updateUserEmail(string memory username, string memory newEmail) public onlyOwner {
        string memory oldEmail = users[username].email;
        users[username].email = newEmail;
        emit UserEmailUpdated(username, oldEmail, newEmail);
    }

    function updateUserFullName(string memory username, string memory newFullName) public onlyOwner {
        string memory oldFullName = users[username].fullName;
        users[username].fullName = newFullName;
        emit UserFullNameUpdated(username, oldFullName, newFullName);
    }

    function toggleUser(string memory username) public onlyOwner {
        users[username].enabled = !users[username].enabled;
        emit UserToggled(username, users[username].enabled);
    }

    function requireUserPasswordChange(string memory username) public onlyOwner {
        users[username].passwordChangeRequired = true;
        emit PasswordChangeRequired(username);
    }

    function checkIfUserExists(string memory username) public view returns (bool) {
        //if a username returns that is longer than 0 characters, it returns true. Usernames of 0 chars means it does not exist, so it would be false.
        return bytes(users[username].username).length > 0;
    }

    function getUser(string memory username) public view returns (string memory, string memory, string[] memory, string memory, string memory, bool, bool, string memory, string memory) {
        User memory user = users[username];
        return (user.username, user.passwordHash, user.faceHashes, user.accountCreationDate, user.lastEditDate, user.faceReenrollmentRequired, user.enabled, user.email, user.fullName);
    }

    function getAllUsernames() public view returns (string[] memory) {
        return allUsernames;
    }

    // Group management functions
    function createGroup(string memory groupName, string[] memory permissions) public onlyOwner {
        groups[groupName] = Group(groupName, new string[](0), permissions);
        allGroupNames.push(groupName);
        emit GroupCreated(groupName, permissions);
    }

    function addUserToGroup(string memory groupName, string memory username) public onlyOwner {
        require(bytes(groups[groupName].name).length > 0, "Group does not exist");
        require(bytes(users[username].username).length > 0, "User does not exist");

        groups[groupName].members.push(username);
        emit UserAddedToGroup(username, groupName);
    }

    function removeUserFromGroup(string memory groupName, string memory username) public onlyOwner {
        require(bytes(groups[groupName].name).length > 0, "Group does not exist");
        require(bytes(users[username].username).length > 0, "User does not exist");

        string[] storage members = groups[groupName].members;
        bool found = false;

        for (uint i = 0; i < members.length; i++) {
            if (keccak256(abi.encodePacked(members[i])) == keccak256(abi.encodePacked(username))) {
                found = true;
                members[i] = members[members.length - 1]; // Move the last element to the found index
                members.pop(); // Remove the last element
                break;
            }
        }

        require(found, "User is not in this group");

        emit UserRemovedFromGroup(username, groupName);
    }

    function getUserPermissions(string memory username) public view returns (string[] memory) {
        require(bytes(users[username].username).length > 0, "User does not exist");
        
        string[] memory userGroups = new string[](allGroupNames.length);
        uint groupCount = 0;
        
        // Identify groups the user belongs to
        for (uint i = 0; i < allGroupNames.length; i++) {
            Group storage group = groups[allGroupNames[i]];
            for (uint j = 0; j < group.members.length; j++) {
                if (keccak256(abi.encodePacked(group.members[j])) == keccak256(abi.encodePacked(username))) {
                    userGroups[groupCount] = group.name;
                    groupCount++;
                    break;
                }
            }
        }

        string[] memory userPermissionsList = new string[](50); // Arbitrary size, can be optimized
        uint permissionCount = 0;
        
        // Aggregate permissions from groups
        for (uint i = 0; i < groupCount; i++) {
            string memory groupName = userGroups[i];
            string[] storage permissions = groups[groupName].permissions;
            for (uint j = 0; j < permissions.length; j++) {
                bool exists = false;
                for (uint k = 0; k < permissionCount; k++) {
                    if (keccak256(abi.encodePacked(userPermissionsList[k])) == keccak256(abi.encodePacked(permissions[j]))) {
                        exists = true;
                        break;
                    }
                }
                if (!exists) {
                    userPermissionsList[permissionCount] = permissions[j];
                    permissionCount++;
                }
            }
        }

        string[] memory finalPermissions = new string[](permissionCount);
        for (uint i = 0; i < permissionCount; i++) {
            finalPermissions[i] = userPermissionsList[i];
        }

        return finalPermissions;
    }

    function getAllGroups() public view returns (string[] memory) {
        return allGroupNames;
    }

    function getGroup(string memory groupName) public onlyOwner view returns (string memory, string[] memory, string[] memory) {
        require(bytes(groups[groupName].name).length > 0, "Group does not exist");
        Group memory group = groups[groupName];
        return (group.name, group.permissions, group.members);
    }

    function updateGroup(string memory originalGroupName, string memory newGroupName, string[] memory newPermissions) public onlyOwner {
        require(bytes(groups[originalGroupName].name).length > 0, "Group does not exist");

        // Define the core groups
        string[4] memory coreGroups = ["Administrators", "Users", "Group Managers", "User Managers"];
        
        // Check if the groupName is in the core groups
        for (uint i = 0; i < coreGroups.length; i++) {
            require(keccak256(abi.encodePacked(originalGroupName)) != keccak256(abi.encodePacked(coreGroups[i])),
                    "Modifying core group permissions is not allowed");
        }

        setGroupPermissions(originalGroupName, newPermissions);

        if(keccak256(abi.encodePacked(originalGroupName)) != keccak256(abi.encodePacked(newGroupName)))
        {
            //move group to new mapping name, copying it's contents
            groups[newGroupName] = groups[originalGroupName];

            // Update the name inside the struct
            groups[newGroupName].name = newGroupName;

            // Delete the old mapping entry, so the old group name can be reused.
            delete groups[originalGroupName];

            // Update the allGroupNames array
            for (uint i = 0; i < allGroupNames.length; i++) {
                if (keccak256(abi.encodePacked(allGroupNames[i])) == keccak256(abi.encodePacked(originalGroupName))) {
                    allGroupNames[i] = newGroupName; // Replace old name with new name
                    break; // Stop looping after finding the match
                }
            }

            emit GroupNameUpdated(originalGroupName, newGroupName);
        }
    }

    function setGroupPermissions(string memory groupName, string[] memory groupPermissions) public onlyOwner returns (string memory) {
        require(bytes(groups[groupName].name).length > 0, "Group does not exist");

        // Define the core groups
        string[4] memory coreGroups = ["Administrators", "Users", "Group Managers", "User Managers"];
        
        // Check if the groupName is in the core groups
        for (uint i = 0; i < coreGroups.length; i++) {
            require(keccak256(abi.encodePacked(groupName)) != keccak256(abi.encodePacked(coreGroups[i])),
                    "Modifying core group permissions is not allowed");
        }

        groups[groupName].permissions = groupPermissions;
        emit GroupPermissionsUpdated(groups[groupName].name, groups[groupName].permissions);
        return groups[groupName].name;
    }

    function removeGroup(string memory groupName) public onlyOwner {
        require(bytes(groups[groupName].name).length > 0, "Group does not exist");

        // Define the core groups
        string[4] memory coreGroups = ["Administrators", "Users", "Group Managers", "User Managers"];
        
        // Check if the groupName is in the core groups
        for (uint i = 0; i < coreGroups.length; i++) {
            require(keccak256(abi.encodePacked(groupName)) != keccak256(abi.encodePacked(coreGroups[i])),
                    "Modifying core group permissions is not allowed");
        }

        // Remove from mapping
        delete groups[groupName];

        // Remove from allGroupNames array
        bool found = false;
        for (uint i = 0; i < allGroupNames.length; i++) {
            if (keccak256(abi.encodePacked(allGroupNames[i])) == keccak256(abi.encodePacked(groupName))) {
                found = true;
                allGroupNames[i] = allGroupNames[allGroupNames.length - 1]; // Move last element to current position
                allGroupNames.pop(); // Remove last element
                break;
            }
        }

        require(found, "Group not found in allGroupNames");

        emit GroupRemoved(groupName);
    }
}