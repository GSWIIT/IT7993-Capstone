import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./permissions.css"
import { Link } from "react-router-dom";
import backgroundvideo from "../assets/backgroundvideo.mp4";
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
  const [editMode, setEditMode] = useState(false);
  const [groupName, setGroupName] = useState("");
  const [permissionsArray, setPermissionsArray] = useState<string[]>([]);
  const [newPermission, setNewPermission] = useState("");
  const [editingGroup, setEditingGroup] = useState<Group | null>(null);

  const [showEditUsersOverlay, setShowEditUsersOverlay] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null);
  const [newUser, setNewUser] = useState("");

  // Server message overlay states
  const [showServerMessage, setShowServerMessage] = useState(false);
  const [serverMessage, setServerMessage] = useState("Loading...");
  const [isLoading, setIsLoading] = useState(true);

  const toggleModal = (group?: Group) => {
    if (group) {
      setEditMode(true);
      setGroupName(group.name);
      setPermissionsArray(group.permissions);
      setEditingGroup(group);
    } else {
      setEditMode(false);
      setGroupName("");
      setPermissionsArray([]);
      setEditingGroup(null);
    }
    setNewPermission("");
    setShowModal(!showModal);
  };

  const handleCreateGroup = async () => {
    setShowModal(false)
    showLoadingOverlay()

    if(editingGroup != null)
    {
      console.log("Update group:", editingGroup.name, " to ", groupName, "with permissions:", permissionsArray);
      await fetch('http://127.0.0.1:5000/permissions/update-group', {
        method: 'POST',
        credentials: "include",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          originalGroupName: editingGroup.name,
          newGroupName: groupName,
          groupPermissions: permissionsArray
        }),
      })
      .then((response) => response.json())
      .then((result) => {
        setIsLoading(false)
        setServerResponseMessage(result.reason)
        if(result.success)
        {
          getGroups()
        }
      })
    }
    else
    {
      console.log("Creating group:", groupName, "with permissions:", permissionsArray);
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
        if(result.success)
        {
          getGroups()
        }
      })
    }
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

  const toggleEditUsersOverlay = (group?: Group) => {
    setSelectedGroup(group || null);
    setShowEditUsersOverlay(!showEditUsersOverlay);
  };

  const handleAddUser = async () => {
    if (newUser.trim() && selectedGroup) {
      showLoadingOverlay()
      await fetch('http://127.0.0.1:5000/permissions/add-group-user', {
        method: 'POST',
        credentials: "include",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          groupName: selectedGroup.name,
          username: newUser.trim()
        }),
      })
      .then((response) => response.json())
      .then((result) => {
        setIsLoading(false)
        setServerResponseMessage(result.reason)
        if(result.success)
        {
          hideLoadingOverlay()
          setSelectedGroup({ ...selectedGroup, members: [...selectedGroup.members, newUser.trim()] });
        }

        setNewUser("");
      })
    }
  };

  const handleDeleteUser = async (usernameToRemove: string) => {
    if (selectedGroup) {
      showLoadingOverlay()
      await fetch('http://127.0.0.1:5000/permissions/remove-group-user', {
        method: 'POST',
        credentials: "include",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          groupName: selectedGroup.name,
          username: usernameToRemove
        }),
      })
      .then((response) => response.json())
      .then((result) => {
        setIsLoading(false)
        setServerResponseMessage(result.reason)
        if(result.success)
        {
          hideLoadingOverlay()
          setSelectedGroup({ ...selectedGroup, members: selectedGroup.members.filter(user => user !== usernameToRemove) });
        }
        
        setNewUser("");
      })
    }
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
          const transformedGroups = result.array.map((group: { members: string | any[]; }) => ({
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

  const deleteGroup = async (groupName: string) => {
    showLoadingOverlay()
    await fetch('http://127.0.0.1:5000/permissions/delete-group', {
      method: 'POST',
      credentials: "include",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        groupName: groupName
      }),
    })
      .then((response) => response.json())
      .then((result) => {
        console.log(result);
        setIsLoading(false);
        setServerResponseMessage(result.reason);
        if (result.success) 
        {
          getGroups();
          hideLoadingOverlay();
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
    handleScrollToSection("users");
  }, []);


  const onLogOutClick = () => {
    console.log("Logging out...");
    fetch('http://127.0.0.1:5000/auth/logoff-session', {
      method: 'GET',
      credentials: "include"
    })
      .then((response) => response.json())
      .then(() => {
        navigator("/")
      })
  };
  const handleScrollToSection = (id: 'users' | 'groups') => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
      setActiveTab(id); // Set the active tab
    }
  };

  return (
    <div>
      <div className="container">
      <span className="icon">
        <h2>
          <span id="logo">FACE</span> Guard
        </h2>
      </span>
      <nav className="navbar">
        <Link to="/home">   
            <a
            className="Home"
            >
            Home
            </a>
        </Link>
       <Link to="/account" >
        <a
          className="Account"
        >
          Account Settings
        </a>
        </Link>
        <a
          className="Groups"
        >
          Groups & Permissions
        </a>
        <Link to="/about">
        <a
          className="About"
        >
          About Us
        </a>
        </Link>
        <a onClick={onLogOutClick}>Log Out</a>
      </nav>
     </div>
    
     <div className="permissions-video-container">
            { <video
                className="permission-background-video"
                autoPlay
                muted
                loop
            >
                <source src={backgroundvideo} type="video/mp4" />

            </video> }
        <div className="permissions-title">
            <h1>Groups and Permissions</h1>
        </div>
        <div className="permissions-container">
        {showEditUsersOverlay && selectedGroup && (
          <div className="modal-overlay">
            <div className="modal-content">
              <h2>Edit Users: {selectedGroup.name}</h2>
              <table className="permissions-table">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Delete</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedGroup.members.map((username, index) => (
                    <tr key={index}>
                      <td>{username}</td>
                      <td>
                        <button className="delete-permission" onClick={() => handleDeleteUser(username)}>Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="permissions_edit_group_users_add_user_container">
                <input
                  type="text"
                  placeholder="Enter username"
                  value={newUser}
                  onChange={(e) => setNewUser(e.target.value)}
                />
                
              </div>
              <div className="modal-buttons">
              <button onClick={handleAddUser} className="permissions_edit_group_users_add_user_button">Add</button>
                <button className="permissions_edit_group_users_submit_button" onClick={() => toggleEditUsersOverlay()}>Done</button>
              </div>
            </div>
          </div>
        )}
        {showModal && (
            <div className="modal-overlay">
              <div className="modal-content">
                <h2>{editMode ? "Edit Group" : "Create a Group"}</h2>
                <div className="add-permissions-container">
                  <input
                    type="text"
                    placeholder="Group Name"
                    value={groupName}
                    onChange={(e) => setGroupName(e.target.value)}
                  />
                  <input
                    type="text"
                    placeholder="Enter permission"
                    value={newPermission}
                    onChange={(e) => setNewPermission(e.target.value)}
                  />
                </div>
                <button onClick={handleAddPermission} className="add-permission-button">Add</button>
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
                <div className="modal-buttons">
                  <button onClick={handleCreateGroup} className="modal-submit">{editMode ? "Save Changes" : "Submit"}</button>
                  <button onClick={() => toggleModal()} className="modal-cancel">Cancel</button>
                </div>
              </div>
            </div>
          )}
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


          <nav className="permissions-navbar">
                    <a
                        className={`user ${activeTab === 'users' ? 'active' : ''}`}
                        onClick={() => handleScrollToSection("users")}
                    >
                    User
                    </a>
                    <a
                        className={`group ${activeTab === 'groups' ? 'active' : ''}`}
                        onClick={() => handleScrollToSection("groups")}
                    >
                    Group
                    </a>
                </nav>
          <div className="permission-content">
            <section id="users" className="main">
              <div className="permissions-table-container">
                <table className="permissions-table">
                  <thead className="permissions-table-head">
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
                <div className="permissions-display-container">
                  <p className="user-permissions">Your Current Permissions:</p>
                  <ul className="user-permissions-list">
                    {userPermissions.map((permission, index) => (
                      <li className="green-li" key={index}>{permission}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </section>
            
            <section id="groups" className="main">
              <div className="permissions-table-container">
                <div className="internal-permission-table-scroller">             
                  <table className="permissions-table">
                    <thead className="permissions-table-head">
                      <tr>
                        <th>Name</th>
                        <th>Permissions</th>
                        <th>Users</th>
                        <th>Edit Users</th>
                        <th>Edit Group</th>
                        <th>Delete</th>
                      </tr>
                    </thead>
                    <tbody>
                      {groups.map((group) => (
                        <tr key={group.name}>
                          <td>{group.name}</td>
                          <td>
                            <ul className="group-permissions-list">
                            {group.permissions.map((permission,index)=>
                              <li className="green-li-group" key={index}>{permission} </li>
                              )}
                            </ul>
                          </td>
                          <td>{group.members.join(', ')}</td>
                          <td>
                          <button className="permissions-edit-button" onClick={() => toggleEditUsersOverlay(group)}>Edit Users</button>
                          </td>
                          <td>
                            <button className="permissions-edit-button" onClick={() => toggleModal(group)}>Edit Group</button>
                          </td>
                          <td>
                            <button className="permissions-edit-button" onClick={() => deleteGroup(group.name)}>Delete</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>   
                <div className="create-group-btn-container">
                  <button className="permissions-create-button" onClick={() => toggleModal()}>Create A Group</button>
                </div>
              </div>
            </section>
          

         
          </div>
        </div>
      </div>
    </div>
  );
};

export default Permissions;