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
    string[] private ownerPermissions;

    address private owner;

    event UserRegistered(string username);
    event PasswordUpdated(string username);
    event PasswordChangeRequired(string username);
    event FaceHashUpdated(string username);
    event PermissionsUpdated(string username);
    event UserToggled(string username, bool enabled);
    event GroupCreated(string groupName);
    event UserAddedToGroup(string username, string groupName);
    event UserRemovedFromGroup(string username, string groupName);
    event GroupPermissionsUpdated(string groupName, string[] permissions);
    event GroupRemoved(string groupName);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the contract owner can perform this action");
        _;
    }

    constructor(string memory creationDate) {
        owner = msg.sender;

        createGroup("Owners");
        createGroup("Administrators");
        createGroup("Users");

        ownerPermissions.push("Full Control");
        setGroupPermissions("Owners", ownerPermissions);
    }

    function registerUser(string memory username, string memory passwordHash, string[] memory initialFaceHashes, string memory creationDate) public onlyOwner {
        users[username] = User(username, passwordHash, initialFaceHashes, creationDate, creationDate, false, false, true);
        allUsernames.push(username);
        addUserToGroup(username, "Users");
        emit UserRegistered(username);

        //if this is the very first user in the smart contract, we will also add them to the owners group and administrators group.
        if (allUsernames.length == 1) {
            addUserToGroup(username, "Owners");
            addUserToGroup(username, "Administrators");
        }
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

    function getUser(string memory username) public view returns (string memory, string memory, string[] memory, string memory, string memory, bool, bool) {
        User memory user = users[username];
        return (user.username, user.passwordHash, user.faceHashes, user.accountCreationDate, user.lastEditDate, user.faceReenrollmentRequired, user.enabled);
    }

    function getAllUsernames() public view returns (string[] memory) {
        return allUsernames;
    }

    // Group management functions
    function createGroup(string memory groupName) public onlyOwner {
        groups[groupName] = Group(groupName, new string[](0), new string[](0));
        allGroupNames.push(groupName);
        emit GroupCreated(groupName);
    }

    function addUserToGroup(string memory username, string memory groupName) public onlyOwner {
        require(bytes(groups[groupName].name).length > 0, "Group does not exist");
        require(bytes(users[username].username).length > 0, "User does not exist");

        groups[groupName].members.push(username);
        emit UserAddedToGroup(username, groupName);
    }

    function removeUserFromGroup(string memory username, string memory groupName) public onlyOwner {
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

    function getAllGroups() public view returns (string[] memory) {
        return allGroupNames;
    }

    function getGroup(string memory groupName) public onlyOwner view returns (string memory, string[] memory, string[] memory) {
        require(bytes(groups[groupName].name).length > 0, "Group does not exist");
        Group memory group = groups[groupName];
        return (group.name, group.permissions, group.members);
    }

    function setGroupPermissions(string memory groupName, string[] memory groupPermissions) public onlyOwner returns (string memory) {
        require(bytes(groups[groupName].name).length > 0, "Group does not exist");
        groups[groupName].permissions = groupPermissions;
        emit GroupPermissionsUpdated(groups[groupName].name, groups[groupName].permissions);
        return groups[groupName].name;
    }

    function removeGroup(string memory groupName) public onlyOwner {
        require(bytes(groups[groupName].name).length > 0, "Group does not exist");

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