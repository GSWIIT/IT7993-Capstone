// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FaceGuard {
    struct User {
        string username;
        string passwordHash;
        string faceHash;
        string[] permissions;
        string applicationKey;
        bool enabled;
    }
    
    mapping(string => User) private users;
    address private owner;
    
    event UserRegistered(string username, string applicationKey);
    event PasswordUpdated(string username);
    event FaceHashUpdated(string username);
    event PermissionsUpdated(string username);
    event UserToggled(string username, bool enabled);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only the contract owner can perform this action");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    function registerUser(string memory username, string memory passwordHash, string memory faceHash, string memory applicationKey) public onlyOwner {
        users[username] = User(username, passwordHash, faceHash, new string[](0), applicationKey, true);
        emit UserRegistered(username, applicationKey);
    }
    
    function updateUserPassword(string memory username, string memory newPasswordHash) public onlyOwner {
        users[username].passwordHash = newPasswordHash;
        emit PasswordUpdated(username);
    }
    
    function updateUserFaceHash(string memory username, string memory newFaceHash) public onlyOwner {
        users[username].faceHash = newFaceHash;
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
    
    function getUser(string memory username) public view returns (string memory, string memory, string memory, string[] memory, string memory, bool) {
        User memory user = users[username];
        return (user.username, user.passwordHash, user.faceHash, user.permissions, user.applicationKey, user.enabled);
    }
}