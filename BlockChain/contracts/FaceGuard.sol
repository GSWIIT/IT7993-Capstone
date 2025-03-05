// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FaceGuard {
    struct User {
        string username;
        string passwordHash;
        string[] faceHashes;
        string[] groups;
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

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the contract owner can perform this action");
        _;
    }

    constructor(string memory creationDate) {
        owner = msg.sender;

        groups["Owners"] = Group("Owners", new string[](0), new string[](0));
        emit GroupCreated("Owners");
        groups["Users"] = Group("Users", new string[](0), new string[](0));
        emit GroupCreated("Users");

        ownerPermissions.push("Full Control");

        setGroupPermissions("Owners", ownerPermissions);
        registerUser("Administrator", "", new string[](0), creationDate);
        requireUserPasswordChange("Administrator");
    }

    function registerUser(string memory username, string memory passwordHash, string[] memory initialFaceHashes, string memory creationDate) public onlyOwner {
        users[username] = User(username, passwordHash, initialFaceHashes, new string[](0), creationDate, creationDate, false, false, true);
        allUsernames.push(username);
        addUserToGroup(username, "Users");
        emit UserRegistered(username);
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

    function getUser(string memory username) public view returns (string memory, string memory, string[] memory, string[] memory, string memory, string memory, bool, bool) {
        User memory user = users[username];
        return (user.username, user.passwordHash, user.faceHashes, user.groups, user.accountCreationDate, user.lastEditDate, user.faceReenrollmentRequired, user.enabled);
    }

    function getAllUsernames() public view returns (string[] memory) {
        return allUsernames;
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

    function setGroupPermissions(string memory groupName, string[] memory groupPermissions) public onlyOwner returns (string memory) {
        require(bytes(groups[groupName].name).length > 0, "Group does not exist");
        groups[groupName].permissions = groupPermissions;
        emit GroupPermissionsUpdated(groups[groupName].name, groups[groupName].permissions);
        return groups[groupName].name;
    }
}