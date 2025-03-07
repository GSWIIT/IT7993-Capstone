import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./permissions.css"

interface Group {
  name: string;
  permissions: string[];
  members: string[];
}

interface User {
  username: string;
  faceHashes: boolean;
  faceReenrollmentRequired: boolean;
  accountCreationDate: string;
  lastEditDate: string;
  assignedGroups: string;
  enabled: boolean;
}

const Permissions: React.FC = () => {
  const navigator = useNavigate()

  const [usersLoaded, setUsersLoaded] = useState(false)
  const [groupsLoaded, setGroupsLoaded] = useState(false)
  const [permissionsLoaded, setPermissionsLoaded] = useState(false)

  const [activeTab, setActiveTab] = useState<'users' | 'groups'>('users');
  const [users, setUsers] = useState<User[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [userPermissions, setPermissions] = useState<string[]>(["None"]);

  const [showModal, setShowModal] = useState(false);
  const [groupName, setGroupName] = useState("");
  const [permissionsArray, setPermissionsArray] = useState<string[]>([]);
  const [newPermission, setNewPermission] = useState("");

  // Server message overlay states
  const [showServerMessage, setShowServerMessage] = useState(false);
  const [serverMessage, setServerMessage] = useState("Loading...");
  const [isLoading, setIsLoading] = useState(true);

  const toggleModal = () => {
    setShowModal(!showModal);
    setGroupName("");
    setPermissionsArray([]);
    setNewPermission("");
  };

  const handleCreateGroup = async () => {
    setShowModal(false)
    console.log("Creating group:", groupName, "with permissions:", permissionsArray);
    showLoadingOverlay()
    await fetch('http://127.0.0.1:5000/permissions/create-group', {
      method: 'POST',
      credentials: "include",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        groupName: groupName,
        groupPermissions: permissionsArray
      }),
    })
    .then((response) => response.json())
    .then((result) => {
      setIsLoading(false)
      setServerResponseMessage(result.reason)
    })
  };

  const handleAddPermission = () => {
    if (newPermission.trim() !== "" && !permissionsArray.includes(newPermission.trim())) {
      setPermissionsArray([...permissionsArray, newPermission.trim()]);
      setNewPermission("");
    }
  };

  const handleDeletePermission = (permission: string) => {
    setPermissionsArray(permissionsArray.filter((perm) => perm !== permission));
  };

  const showLoadingOverlay = () => {
    setIsLoading(true);
    setServerMessage("Loading...");
    setShowServerMessage(true);
    console.log("Showing loading overlay...")
  };

  const hideLoadingOverlay = () => {
    setShowServerMessage(false);
  };

  const setServerResponseMessage = (message: string) => {
    setIsLoading(false);
    setServerMessage(message);
  };

  const checkSession = async () => {
    await fetch('http://127.0.0.1:5000/auth/check-session', {
      method: 'GET',
      credentials: "include"
    })
    .then((response) => response.json())
    .then((result) => {
      if(result.logged_in == false)
      {
        console.log("No login session detected!")
        navigator("/")
      }
      else
      {
        console.log("Session: ", result)
      }
    })
  };

  const getUsers = async () => {
    await fetch('http://127.0.0.1:5000/permissions/get-users', {
      method: 'GET',
      credentials: "include"
    })
      .then((response) => response.json())
      .then((result) => {
        console.log(result);
        if (result.success) 
        {
          setUsers(result.array)
          setUsersLoaded(true)
          if(usersLoaded && groupsLoaded && permissionsLoaded)
          {
            hideLoadingOverlay();
          }
        }
      });
  }

  const getGroups = async () => {
    await fetch('http://127.0.0.1:5000/permissions/get-groups', {
      method: 'GET',
      credentials: "include"
    })
      .then((response) => response.json())
      .then((result) => {
        console.log(result);
        if (result.success) 
        {
          // Transform the groups data in case there are too many usernames (it keeps the UI from clogging up)
          const transformedGroups = result.array.map(group => ({
            ...group,
            members: group.members.length > 3 
              ? [...group.members.slice(0, 3), "..."] 
              : group.members
          }));
          setGroups(transformedGroups)
          setGroupsLoaded(true)
          if(usersLoaded && groupsLoaded && permissionsLoaded)
          {
              hideLoadingOverlay();
          }
        }
      });
  }

  const getPermissions = async () => {
    await fetch('http://127.0.0.1:5000/permissions/get-user-permissions', {
      method: 'GET',
      credentials: "include"
    })
      .then((response) => response.json())
      .then((result) => {
        console.log(result);
        if (result.success) 
        {
          setPermissions(result.array)
          hideLoadingOverlay();
          setPermissionsLoaded(true)
          if(usersLoaded && groupsLoaded && permissionsLoaded)
          {
            hideLoadingOverlay();
          }
        }
      });
  }

  useEffect(() => {
    showLoadingOverlay();
    checkSession();
    getUsers();
    getGroups();
    getPermissions();
  }, []);

  return (
    <div className="permissions-container">
      {showServerMessage && (
        <div className="server-message-overlay">
          <div className="server-message-box">
            {isLoading ? (
              <>
                <div className="loading-spinner"></div>
                <p>{serverMessage}</p>
              </>
            ) : (
              <>
                <p>{serverMessage}</p>
                <button onClick={hideLoadingOverlay} className="ok-button">OK</button>
              </>
            )}
          </div>
        </div>
      )}

      <div className="permissions-tabs">
        <button className={`permissions-tab ${activeTab === 'users' ? 'active' : ''}`} onClick={() => setActiveTab('users')}>Users</button>
        <button className={`permissions-tab ${activeTab === 'groups' ? 'active' : ''}`} onClick={() => setActiveTab('groups')}>Groups</button>
      </div>
      
      {activeTab === 'users' ? (
        <div className="permissions-table-container">
          <div>
            <h2>User Information</h2>
            <p>Note: Your permission level impacts this view!</p>
            <p>Your Current Permissions: {userPermissions.join(', ')}</p>
          </div>
          <table>
            <thead>
              <tr>
                <th>Username</th>
                <th>Face Hashes</th>
                <th>Face Re-Enrollment Required</th>
                <th>Account Creation Date</th>
                <th>Last Edit Date</th>
                <th>Enabled</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.username}>
                  <td>{user.username}</td>
                  <td>{`${user.faceHashes}`}</td>
                  <td>{`${user.faceReenrollmentRequired}`}</td>
                  <td>{user.accountCreationDate}</td>
                  <td>{user.lastEditDate}</td>
                  <td>{`${user.enabled}`}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="permissions-table-container">
          <div>
            <h2>Group Information</h2>
            <p>Note: Your permission level impacts this view!</p>
          </div>
          <button className="permissions-create-button" onClick={toggleModal}>Create A Group</button>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Permissions</th>
                <th>Users</th>
                <th>Edit Group</th>
              </tr>
            </thead>
            <tbody>
              {groups.map((group) => (
                <tr key={group.name}>
                  <td>{group.name}</td>
                  <td>{group.permissions.join(', ')}</td>
                  <td>{group.members.join(', ')}</td>
                  <td>
                    <button className="permissions-edit-button" onClick={() => alert(`Edit group with GUID: ${group.name}`)}>Edit</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Create a Group</h2>
            <input
              type="text"
              placeholder="Group Name"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
            />
            
            <table className="permissions-table">
              <thead>
                <tr>
                  <th>Permission Name</th>
                  <th>Delete</th>
                </tr>
              </thead>
              <tbody>
                {permissionsArray.map((permission, index) => (
                  <tr key={index}>
                    <td>{permission}</td>
                    <td>
                      <button className="delete-permission" onClick={() => handleDeletePermission(permission)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="add-permission-container">
              <input
                type="text"
                placeholder="Enter permission"
                value={newPermission}
                onChange={(e) => setNewPermission(e.target.value)}
              />
              <button onClick={handleAddPermission} className="add-permission-button">Add</button>
            </div>

            <div className="modal-buttons">
              <button onClick={handleCreateGroup} className="modal-submit">Submit</button>
              <button onClick={toggleModal} className="modal-cancel">Cancel</button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default Permissions;