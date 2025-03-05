import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./permissions.css"
import { stringify } from "postcss";
interface Group {
  id: string;
  name: string;
  permissions: string;
  userCount: number;
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

  const [groups, setGroups] = useState<Group[]>([
    { id: "123e4567-e89b-12d3-a456-426614174000", name: "Admin Group", permissions: "Read, Write, Execute", userCount: 5 },
    { id: "987f6543-b21a-98c7-d654-789012345678", name: "User Group", permissions: "Read, Execute", userCount: 10 },
    { id: "555a444b-c333-d222-e111-000999888777", name: "Guest Group", permissions: "Read Only", userCount: 3 },
  ]);

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

  useEffect(() => {
    checkSession();
    getUsers();    
  }, []);

  return (
    <div className="permissions-container">
      <div className="permissions-tabs">
        <button className={`permissions-tab ${activeTab === 'users' ? 'active' : ''}`} onClick={() => setActiveTab('users')}>Users</button>
        <button className={`permissions-tab ${activeTab === 'groups' ? 'active' : ''}`} onClick={() => setActiveTab('groups')}>Groups</button>
      </div>
      
      {activeTab === 'users' ? (
        <div className="permissions-table-container">
          <table>
            <thead>
              <tr>
                <th>Username</th>
                <th>Face Hashes</th>
                <th>Face Re-Enrollment Required</th>
                <th>Account Creation Date</th>
                <th>Last Edit Date</th>
                <th>Assigned Groups</th>
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
                  <td>{user.assignedGroups}</td>
                  <td>{`${user.enabled}`}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="permissions-table-container">
          <button className="permissions-create-button">Create A Group</button>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Permissions</th>
                <th># of Users</th>
                <th>View GUID</th>
                <th>Edit</th>
              </tr>
            </thead>
            <tbody>
              {groups.map((group) => (
                <tr key={group.id}>
                  <td>{group.name}</td>
                  <td>{group.permissions}</td>
                  <td>{group.userCount}</td>
                  <td>
                    <button className="permissions-view-button" onClick={() => alert(`GUID: ${group.id}`)}>View GUID</button>
                  </td>
                  <td>
                    <button className="permissions-edit-button" onClick={() => alert(`Edit group with GUID: ${group.id}`)}>Edit</button>
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