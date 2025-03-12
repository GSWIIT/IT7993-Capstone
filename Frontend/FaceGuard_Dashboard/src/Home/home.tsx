import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./home.css";
import { Link } from "react-router-dom";
import backgroundvideo from "../assets/backgroundvideo.mp4";

const home: React.FC = () => {
  const navigator = useNavigate()
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
        window.location.href = '';
      })
  };

  useEffect(() => {
    checkSession()
  }, [])

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
                <Link to="/permissions">
                  <a
                    className="Groups"
                  >
                    Groups & Permissions
                  </a>
                </Link>
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
    
     <div className="video-container">
            <video
                className="autoplay muted loop"
                autoPlay
                muted
                loop
            >
                <source src={backgroundvideo} type="video/mp4" />

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
