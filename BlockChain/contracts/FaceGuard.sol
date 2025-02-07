// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FaceGuard {
    struct User {
        string fullName;
        string username;
        string facialHash;
    }

    mapping(string => User) private users;
    mapping(string => bool) private usernameExists;
    address public owner;

    event UserRegistered(string username, string fullName);

    // Constructor: Initializes the contract with the deployer as the first user (optional)
    constructor(string memory _fullName, string memory _username, string memory _facialHash) {
        require(bytes(_fullName).length > 0, "Full name is required");
        require(bytes(_username).length > 0, "Username is required");
        require(bytes(_facialHash).length > 0, "Facial hash is required");

        owner = msg.sender; // Set contract deployer as the owner
        users[_username] = User(_fullName, _username, _facialHash);
        usernameExists[_username] = true;

        emit UserRegistered(_username, _fullName);
    }

    function registerUser(string memory _fullName, string memory _username, string memory _facialHash) public {
        require(bytes(_fullName).length > 0, "Full name is required");
        require(bytes(_username).length > 0, "Username is required");
        require(bytes(_facialHash).length > 0, "Facial hash is required");
        require(!usernameExists[_username], "Username already exists");

        users[_username] = User({
            fullName: _fullName,
            username: _username,
            facialHash: _facialHash
        });

        usernameExists[_username] = true;

        emit UserRegistered(_username, _fullName);
    }

    function getUserByUsername(string memory _username) public view returns (string memory, string memory, string memory) {
        require(usernameExists[_username], "User not found");

        User memory user = users[_username];
        return (user.fullName, user.username, user.facialHash);
    }
}