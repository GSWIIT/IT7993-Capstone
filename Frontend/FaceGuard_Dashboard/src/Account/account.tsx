import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./account.css";
import backgroundvideo from "../assets/backgroundvideo.mp4";
import { Link } from "react-router-dom";

const account: React.FC = () => {
  const navigator = useNavigate();

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [activeTab, setActiveTab] = useState<'profile' | 'password' | 'facereg' | 'delete'>('profile');

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

  const handleScrollToSection = (id: 'profile' | 'password' | 'facereg' | 'delete') => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
      setActiveTab(id); // Set the active tab
    }
  };

  const onSaveNameClick = () => {
    fetch('http://127.0.0.1:5000/account/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: "include",
      body: JSON.stringify({ first_name: firstName, last_name: lastName }),
    })
    .then((response) => response.json())
    .then((result) => {
      if (result.success) {
        console.log("Names saved successfully.");
      } else {
        console.error("Error saving names:", result.reason);
      }
    });
  };

  useEffect(() => {
    checkSession();
    handleScrollToSection("profile");
  }, []);

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
            // onClick={() => handleNavigation("Home")}
            >
            Home
            </a>
        </Link>
        <a
          className="Account"
         // onClick={() => handleNavigation("Account")}
        >
          Account Settings
        </a>
        <Link to="/permissions" className="Groups" >Groups & Permissions</Link>
        <a
          className="About"
         // onClick={() => handleNavigation("Appointment")}
        >
          About Us
        </a>
      
        <a onClick={onLogOutClick}>Log Out</a>
      </nav>
     </div>
    
     <div className="video-container">
            <video
                className="autoplay muted loop"
                autoPlay
                muted
                loop
            >
                <source src={backgroundvideo} type="video/mp4" />

            </video>
            <div className="title">
                <h1>Account Settings</h1>
            </div>
            <div className="content-container">
               <nav className="account-navbar">
                    <a
                        className={`profile ${activeTab === 'profile' ? 'active' : ''}`}
                        onClick={() => handleScrollToSection("profile")}
                    >
                    Profile
                    </a>
                    <a
                        className={`password ${activeTab === 'password' ? 'active' : ''}`}
                        onClick={() => handleScrollToSection("password")}
                    >
                    Password
                    </a>
                    <a
                        className={`facereg ${activeTab === 'facereg' ? 'active' : ''}`}
                        onClick={() => handleScrollToSection("facereg")}
                    >
                    Facial Recognition
                    </a>
                    <a
                        className={`delete ${activeTab === 'delete' ? 'active' : ''}`}
                        onClick={() => handleScrollToSection("delete")}
                    >
                    Delete Account
                    </a>
                </nav>
                <div className="content">
                 <section id="profile" className="main">
                    <header className="major">
                      <h2>Edit Profile</h2>
                    </header>
                    <div className="profile-container">
                      <input 
                        className="firstname-txt" 
                        type="text" 
                        placeholder="Firstname" 
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                      />
                      <input 
                        className="lastname-txt" 
                        type="text" 
                        placeholder="Lastname" 
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                      />
                    </div>
                    <br></br>
                    <button className="profile-btn" onClick={onSaveNameClick}>Submit</button>
							    </section>

                  <section id="password" className="main">
                    <header className="major">
                      <h2>Change Password</h2>
                    </header>
                    <div className="password-container">
                      <input className="current-password-txt" type="text" placeholder="Current Password" />
                      <input className="new-password-txt" type="text" placeholder="New Password" />
                      <input className="confirm-password-txt" type="text" placeholder="Confirm New Password" />
                    </div>
                    <br></br>
                    <button className="password-btn">Submit</button>
              </section>

               <section id="facereg" className="main">
                    <header className="major">
                      <h2>Re-register Facial Recognition</h2>
                    </header>
                    <button className="facereg-btn">Get Started!</button>
							</section> 

               <section id="delete" className="main">
                    <header className="major">
                      <h2>Delete Your Account</h2>
                    </header>
                    <p>Are you sure you want to delete your account? This action cannot be undone.</p>
                    <br></br>
                    <button className="delete-btn">Delete Account</button>
							</section>  


              </div>
            </div>
        </div>

    </div>    
  );
};

export default account;
