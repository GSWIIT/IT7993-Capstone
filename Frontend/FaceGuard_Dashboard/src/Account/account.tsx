import React, { useState, useEffect } from "react";
import "./account.css";
import backgroundvideo from "../assets/backgroundvideo.mp4";
import { Link } from "react-router-dom";

const home: React.FC = () => {
  
  const onLogOutClick = () => {
    console.log("Logging out...");
    // Add logout logic here
  };

  const handleScrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
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
        <a
          className="Groups"
        //  onClick={() => handleNavigation("Posts")}
        >
          Group
        </a>
        <a
          className="About"
         // onClick={() => handleNavigation("Appointment")}
        >
          About
        </a>
      
        //<a onClick={onLogOutClick}>Log Out</a>
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
                        className="profile"
                        onClick={() => handleScrollToSection("profile")}
                    >
                    Profile
                    </a>
                    <a
                        className="password"
                        onClick={() => handleScrollToSection("password")}
                    >
                    Password
                    </a>
                    <a
                        className="facereg"
                        onClick={() => handleScrollToSection("facereg")}
                    >
                    Facial Recognition
                    </a>
                    <a
                        className="delete"
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
                      <input className="firstname-txt" type="text" placeholder="Firstname" />
                      <input className="lastname-txt" type="text" placeholder="Lastname" />
                    </div>
                    <button className="profile-btn">Submit</button>
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
                      <h2>Facial Recognition</h2>
                    </header>
                    <p>Re-register Facial Recognition</p>
                    <br></br>
                    <button className="facereg-btn">Start</button>
							</section> 

               <section id="delete" className="main">
                    <header className="major">
                      <h2>Delete Account</h2>
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

export default home;
