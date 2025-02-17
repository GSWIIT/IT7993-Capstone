// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FaceGuard {
    struct User {
        string username;
        string passwordHash;
        bytes32[] faceHashes;
        string[] permissions;
        string applicationKey;
        bool enabled;
    }

    struct Group {
        string name;
        string[] members;
        string[] permissions;
    }

    mapping(string => User) private users;
    mapping(string => Group) private groups;

    address private owner;

    event UserRegistered(string username, string applicationKey);
    event PasswordUpdated(string username);
    event FaceHashUpdated(string username);
    event PermissionsUpdated(string username);
    event UserToggled(string username, bool enabled);
    event GroupCreated(string groupName);
    event UserAddedToGroup(string username, string groupName);
    event UserRemovedFromGroup(string username, string groupName);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the contract owner can perform this action");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function registerUser(string memory username, string memory passwordHash, bytes32[] memory initialFaceHashes, string memory applicationKey) public onlyOwner {
        users[username] = User(username, passwordHash, initialFaceHashes, new string[](0), applicationKey, true);
        emit UserRegistered(username, applicationKey);
    }

    function getUserFaceHashes(string memory username) public view returns (bytes32[] memory) {
        return users[username].faceHashes;
    }

    function updateUserPassword(string memory username, string memory newPasswordHash) public onlyOwner {
        users[username].passwordHash = newPasswordHash;
        emit PasswordUpdated(username);
    }

    function updateUserFaceHash(string memory username, bytes32[] memory newFaceHashes) public onlyOwner {
        users[username].faceHashes = newFaceHashes;
        emit FaceHashUpdated(username);
    }

    function editUserPermissions(string memory username, string[] memory newPermissions) public onlyOwner {
        users[username].permissions = newPermissions;
        emit PermissionsUpdated(username);
    }

    function toggleUser(string memory username) public onlyOwner {
        users[username].enabled = !users[username].enabled;
        emit UserToggled(username, users[username].enabled);
    }

    function checkIfUserExists(string memory username) public view returns (bool) {
        //if a username returns that is longer than 0 characters, it returns true. Usernames of 0 chars means it does not exist, so it would be false.
        return bytes(users[username].username).length > 0;
    }

    function getUser(string memory username) public view returns (string memory, string memory, bytes32[] memory, string[] memory, string memory, bool) {
        User memory user = users[username];
        return (user.username, user.passwordHash, user.faceHashes, user.permissions, user.applicationKey, user.enabled);
    }

    // Group management functions
    function createGroup(string memory groupName, string memory groupCreator) public onlyOwner {
        groups[groupName] = Group(groupName, new string[](0), new string[](0));
        emit GroupCreated(groupName);
    }

    function addUserToGroup(string memory username, string memory groupName) public onlyOwner {
        require(bytes(groups[groupName].name).length > 0, "Group does not exist");
        require(bytes(users[username].username).length > 0, "User does not exist");

        groups[groupName].members.push(username);
        emit UserAddedToGroup(username, groupName);
    }

    function getGroup(string memory groupName) public view returns (string memory, string[] memory, string[] memory) {
        require(bytes(groups[groupName].name).length > 0, "Group does not exist");
        Group memory group = groups[groupName];
        return (group.name, group.members, group.permissions);
    }
}