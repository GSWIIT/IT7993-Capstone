import React, { useState } from "react";
import "./account.css";

import backgroundvideo from "../assets/backgroundvideo.mp4";
import { Link } from "react-router-dom";

const home: React.FC = () => {
  
  const onLogOutClick = () => {
    console.log("Logging out...");
    // Add logout logic here
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
                    <a href="#profile"
                        className="profile"
                    >
                    Profile
                    </a>
                    <a href="#password"
                        className="Password"
                    >
                    Password
                    </a>
                    <a
                        className="Groups"
                    >
                    Facial Recognition
                    </a>
                    <a
                        className="Groups"
                    >
                    Delete Account
                    </a>
                </nav>
                 <section id="profile" className="main">
                    <div className="spotlight">
                      <div className="content">
                        <header className="major">
                          <h2>Ipsum sed adipiscing</h2>
                        </header>
                        <ul className="actions">
                          <li><a href="generic.html" className="button">Learn More</a></li>
                        </ul>
                      </div>
                      <span className="image"><img src="images/pic01.jpg" alt="" /></span>
                    </div>
							    </section>

                  <section id="password" className="main special">
                    <header className="major">
                      <h2>Magna veroeros</h2>
                    </header>
                    <ul className="features">
                      <li>
                        <span className="icon solid major style1 fa-code"></span>
                        <h3>Ipsum consequat</h3>
                        <p>Sed lorem amet ipsum dolor et amet nullam consequat a feugiat consequat tempus veroeros sed consequat.</p>
                      </li>
                      <li>
                        <span className="icon major style3 fa-copy"></span>
                        <h3>Amed sed feugiat</h3>
                        <p>Sed lorem amet ipsum dolor et amet nullam consequat a feugiat consequat tempus veroeros sed consequat.</p>
                      </li>
                      <li>
                        <span className="icon major style5 fa-gem"></span>
                        <h3>Dolor nullam</h3>
                        <p>Sed lorem amet ipsum dolor et amet nullam consequat a feugiat consequat tempus veroeros sed consequat.</p>
                      </li>
                    </ul>
                    <footer className="major">
                      <ul className="actions special">
                        <li><a href="generic.html" className="button">Learn More</a></li>
                      </ul>
                    </footer>
							</section> 

            </div>
        </div>

    </div>    
  );
};

export default home;
