import React, { useState } from "react";
import "./home.css";
import { Link } from "react-router-dom";
import backgroundvideo from "../assets/backgroundvideo.mp4";

const home: React.FC = () => {
  const checkSession = async () => {
    const response = await fetch("http://127.0.0.1:5000/session/checksession", {
      method: "GET",
      credentials: "include", // Send session cookies
    });
  
    if (response.ok) {
      console.log(response.json())
      return await response.json(); // Get user info
    } else {
      return null;
    }
  };
  
  const onLogOutClick = () => {
    console.log("Logging out...");
    // Add logout logic here
  };

  checkSession()

  return (
    <div> 
      <div className="container">
        <span className="icon">
          <h2>
            <span id="logo">FACE</span> Guard
          </h2>
        </span>
        <nav className="navbar">
          <a
            className="Home"
          // onClick={() => handleNavigation("Home")}
          >
            Home
          </a>
          <Link to="/account"><a
            className="Account"
          // onClick={() => handleNavigation("Account")}
          >
            Account Settings
            
          </a></Link>
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
                Your browser does not support HTML5 video.
            </video>

            <div className="content-home">
                <h1>Welcome to FaceGuard</h1>
                <Link to="/account">
                    <button className="account-btn">Go to Account</button>
                </Link>
            </div>
        </div>

    </div>    
  );
};

export default home;
