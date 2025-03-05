import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./permissions.css"
import { stringify } from "postcss";
interface Group {
  name: string;
  permissions: string;
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

  const [activeTab, setActiveTab] = useState<'users' | 'groups'>('users');

  const [users, setUsers] = useState<User[]>([]);

  const [groups, setGroups] = useState<Group[]>([]);

  const [userPermissions, setPermissions] = useState<string>();

  const checkSession = async () => {
    fetch('http://127.0.0.1:5000/auth/check-session', {
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

  const getUsers = (() => {
    fetch('http://127.0.0.1:5000/permissions/get-users', {
      method: 'GET',
      credentials: "include"
    })
      .then((response) => response.json())
      .then((result) => {
        console.log(result);
        if (result.success) 
        {
          setUsers(result.array)
        }
      });
  })

  const getGroups = (() => {
    fetch('http://127.0.0.1:5000/permissions/get-groups', {
      method: 'GET',
      credentials: "include"
    })
      .then((response) => response.json())
      .then((result) => {
        console.log(result);
        if (result.success) 
        {
          setGroups(result.array)
        }
      });
  })

  const getPermissions = (() => {
    fetch('http://127.0.0.1:5000/permissions/get-user-permissions', {
      method: 'GET',
      credentials: "include"
    })
      .then((response) => response.json())
      .then((result) => {
        console.log(result);
        if (result.success) 
        {
          let permissionsString = ""
          for (let i = 0; i < result.array.length; i++)
          {
            permissionsString += result.array[i];
            if(i < result.array.length - 1)
            {
              permissionsString += ", "
            }
            else
            {
              permissionsString += "."
            }
          }
          setPermissions(permissionsString)
        }
      });
  })

  useEffect(() => {
    checkSession();
    getUsers();
    getGroups();
    getPermissions();
  }, []);

  return (
    <div className="permissions-container">
      <div className="permissions-tabs">
        <button className={`permissions-tab ${activeTab === 'users' ? 'active' : ''}`} onClick={() => setActiveTab('users')}>Users</button>
        <button className={`permissions-tab ${activeTab === 'groups' ? 'active' : ''}`} onClick={() => setActiveTab('groups')}>Groups</button>
      </div>
      
      {activeTab === 'users' ? (
        <div className="permissions-table-container">
          <div>
            <h2>Your User(s)</h2>
            <p>Note: Your permission level impacts this view!</p>
            <p>Your Current Permissions: {userPermissions}</p>
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
            <h2>Your Group(s)</h2>
            <p>Note: Your permission level impacts this view!</p>
          </div>
          <button className="permissions-create-button">Create A Group</button>
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
                  <td>{group.permissions}</td>
                  <td>{group.members}</td>
                  <td>
                    <button className="permissions-edit-button" onClick={() => alert(`Edit group with GUID: ${group.name}`)}>Edit</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Permissions;