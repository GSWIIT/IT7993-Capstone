import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./home.css";
import { Link } from "react-router-dom";
import backgroundvideo from "../assets/backgroundvideo.mp4";

const home: React.FC = () => {
  const navigator = useNavigate()
  const BACKEND_API_DOMAIN_NAME = import.meta.env.VITE_BACKEND_API_DOMAIN_NAME;

  interface QuickLink {
    name: string;
    url: string;
  }

  const [links, setLinks] = useState<QuickLink[]>([]);

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

  const getAllQuickURLLinks = () => {
    fetch(`${BACKEND_API_DOMAIN_NAME}/permissions/get-all-quick-url-links`, {
      method: 'GET',
      credentials: "include"
    })
      .then((response) => response.json())
      .then((result) => {
        console.log(result)
        const mappedLinks: QuickLink[] = result.array.map((item: [string, string]) => ({
          name: item[0],
          url: item[1],
        }));
        setLinks(mappedLinks)
        console.log(links)
      })
  };

  useEffect(() => {
    checkSession()
    getAllQuickURLLinks()
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
                {/* <Link to="/account">
                    <button className="account-btn">Go to Account</button>
                </Link> */}

              <div className="quick-link-container">

                {links.map((link, index) => {
                    const normalizedLink = link.url.startsWith("http://") || link.url.startsWith("https://")
                    ? link.url
                    : `https://${link.url}`;

                  return (
                  <button key={index} onClick={() => window.open(normalizedLink.toString(), "_blank")} type="button" className="quick-link-btn">
                    {links[index].name}
                  </button>
                );
              })}
              </div>
            </div>
        </div>

    </div>    
  );
};

export default home;
