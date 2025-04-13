import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./about.css";
import backgroundvideo from "../assets/backgroundvideo.mp4";
import { Link } from "react-router-dom";
import alchemyLogo from "../assets/Alchemy.png";
import ethereumLogo from "../assets/ethereum-text.png";
import openCVLogo from "../assets/OpenCV.png";

const about: React.FC = () => {
  const navigator = useNavigate();
  const BACKEND_API_DOMAIN_NAME = import.meta.env.VITE_BACKEND_API_DOMAIN_NAME;

  const checkSession = async () => {
    fetch(`${BACKEND_API_DOMAIN_NAME}/auth/check-session`, {
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
    fetch(`${BACKEND_API_DOMAIN_NAME}/auth/logoff-session`, {
      method: 'GET',
      credentials: "include"
    })
      .then((response) => response.json())
      .then(() => {
        window.location.href = '';
      })
  };

  useEffect(() => {
    checkSession();
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
            <a className="Home">Home</a>
          </Link>
          <Link to="/account">
            <a className="Account">Account Settings</a>
          </Link>
          <Link to="/permissions">
            <a className="Groups">Groups & Permissions</a>
          </Link>
          <Link to="/about">
            <a className="About">About Us</a>
          </Link>
          <a onClick={onLogOutClick}>Log Out</a>
        </nav>
      </div>

      <div className="video-container">
        <video className="autoplay muted loop" autoPlay muted loop>
          <source src={backgroundvideo} type="video/mp4" />
        </video>
        <div className="title">
          <h1>About Us</h1>
        </div>
        <div className="about-content-container">
          <div className="about-content">
            <h2 className="about-title">FaceGuard</h2>
            <br></br>
            <p>
              At <strong >FaceGuard</strong>, we are a team of passionate innovators committed to
              revolutionizing enterprise security through cutting-edge
              technology. Our mission is to redefine access management by
              integrating the power of facial recognition and blockchain
              technology, ensuring a secure, seamless, and user-friendly
              authentication system for modern enterprises.
            </p>
            <br></br>
            <p>
              FaceGuard is a Blockchain-Enabled Facial Identification System
              designed to provide secure, tamper-resistant, and efficient
              enterprise access management. By leveraging <strong>OpenCV</strong> for facial
              recognition, <strong>Ethereum</strong> for decentralized security, and <strong>Alchemy</strong> for
              seamless blockchain interactions, we eliminate the vulnerabilities
              of traditional authentication systems while giving users complete
              control over their account.
            </p>
            <br></br>
            <p>
              <div className="about-pics">
                <ul className="about-list">
                  <li>
                    <img src={openCVLogo} alt="opencv" />
                  </li>
                  <li>
                    <img
                      width="250px"
                      src={ethereumLogo}
                      alt="ethereum"
                    />
                  </li>
                  <li>
                    <img
                      width="140px"
                      src={alchemyLogo}
                      alt="alchemy"
                    />
                  </li>
                </ul>
              </div>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default about;
