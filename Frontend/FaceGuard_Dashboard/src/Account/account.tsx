import React, { useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./account.css";
import backgroundvideo from "../assets/backgroundvideo.mp4";
import { Link } from "react-router-dom";

const account: React.FC = () => {
  const pageNavigator = useNavigate();
  const BACKEND_API_DOMAIN_NAME = import.meta.env.VITE_BACKEND_API_DOMAIN_NAME;

  interface Logs {
    block: string;
    data: string;
    event: string;
    timestamp: string;
  }

  // Refs for webcam and canvas elements
  const videoRef = useRef<HTMLVideoElement>(null!);
  const canvas1Ref = useRef<HTMLCanvasElement>(null!);
  const canvas2Ref = useRef<HTMLCanvasElement>(null!);
  const canvas3Ref = useRef<HTMLCanvasElement>(null!);

  // State to control overlay display sections
  const [showCaptureContainer, setShowCaptureContainer] = useState(true);
  const [showPhotoContainer, setShowPhotoContainer] = useState(false);
  const [showFinalPhotoConfirmation, setShowFinalPhotoConfirmation] = useState(false);
  const [showPhotoUploadOverlay, setShowPhotoUploadOverlay] = useState(false);
  const [faceRecognitionMessage, setFaceRecognitionMessage] = useState('');
  const [faceRecognitionSuccess, setFaceRecognitionSuccess] = useState(false);
  const [showFaceRecognitionMessage, setShowFaceRecognitionMessage] = useState(false);

  const [photosTaken, setPhotosTaken] = useState(0);
  const [photoArray, setPhotoArray] = useState<string[]>([]);
  const [confirmedUniqueUsername, setConfirmedUniqueUsername] = useState(false);
  const [confirmedPhotos, setConfirmedPhotos] = useState(false);

  // Server message overlay states
  const [showServerMessage, setShowServerMessage] = useState(false);
  const [serverMessage, setServerMessage] = useState("Loading...");
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(null);

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmNewPassword, setConfirmNewPassword] = useState("");
  const [activeTab, setActiveTab] = useState<'profile' | 'password' | 'facereg' | 'delete' | 'activities'>('profile');

  const [logs, setLogs] = useState<Logs[]>([]);

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
        pageNavigator("/")
      }
      else
      {
        console.log("Session: ", result)
      }
    })
  };

  const capturePhoto = () => {
    if (photosTaken >= 3) {
      setPhotosTaken(0);
    }
  
    setShowPhotoContainer(true); // Ensure canvas is rendered
  
    setTimeout(() => {
      const canvasRefToUse =
        photosTaken === 0 ? canvas1Ref :
        photosTaken === 1 ? canvas2Ref :
        photosTaken === 2 ? canvas3Ref : null;
  
      if (canvasRefToUse?.current && videoRef.current) {
        const context = canvasRefToUse.current.getContext('2d');
        if (context) {
          context.drawImage(
            videoRef.current,
            0,
            0,
            canvasRefToUse.current.width,
            canvasRefToUse.current.height
          );
        }
      }
    }, 200); // Small delay to allow rendering
  
    setPhotosTaken((prev) => prev + 1);
  };

  const startWebcamCapture = async () => {
    console.log("Waiting for video element to be ready...");

    // Wait for video element to be ready
    await waitForVideoElement();

    console.log("videoRef is ready:", videoRef.current);

    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((stream) => {
        console.log("Webcam access granted.");
        videoRef.current!.srcObject = stream;
        videoRef.current!.play();
      })
      .catch((err) => {
        console.error("Error accessing webcam:", err);
        alert("Unable to access webcam.");
      });
  };

  // Function to wait until the video element is available
  const waitForVideoElement = () => {
    return new Promise<void>((resolve) => {
      const interval = setInterval(() => {
        if (videoRef.current) {
          clearInterval(interval);
          resolve();
        }
      }, 100); // Check every 100ms
    });
  };

  const displayCapturePhotoOverlay = () => {
    setShowFinalPhotoConfirmation(false);
    setShowCaptureContainer(true);
    setShowPhotoContainer(false);
    setShowPhotoUploadOverlay(true);
    startWebcamCapture();
  };

  const resetSignUpPhotos = () => {
    [canvas1Ref, canvas2Ref, canvas3Ref].forEach((ref) => {
      if (ref.current) {
        const ctx = ref.current.getContext('2d');
        ctx?.clearRect(0, 0, ref.current.width, ref.current.height);
      }
    });
    setPhotoArray([]);
    setPhotosTaken(0);
    setConfirmedPhotos(false);
    displayCapturePhotoOverlay();
  };

  const displayFaceRecognitionMessage = (message: string, success: boolean) => {
    setFaceRecognitionMessage(message);
    setFaceRecognitionSuccess(success);
    setShowFaceRecognitionMessage(true);
    
  };

  const uploadForRecognition = () => {
    if (photosTaken < 3) {
      displayFaceRecognitionMessage('Error: Three photos are required!', false);
      return;
    }
    const base64Image1 =
      canvas1Ref.current?.toDataURL('image/png').split(',')[1] || '';
    const base64Image2 =
      canvas2Ref.current?.toDataURL('image/png').split(',')[1] || '';
    const base64Image3 =
      canvas3Ref.current?.toDataURL('image/png').split(',')[1] || '';
    const photos = [base64Image1, base64Image2, base64Image3];
    setPhotoArray(photos);

    fetch(`${BACKEND_API_DOMAIN_NAME}/auth/checkface`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ faceArray: photos }),
    })
      .then((response) => response.json())
      .then((result) => {
        displayFaceRecognitionMessage(result.reason, result.success);
        console.log(result.output);
        if (result.success) {
          setConfirmedPhotos(true);
          setShowFinalPhotoConfirmation(true);
          setShowCaptureContainer(false);

        }
        if (result.output) {
          result.output.forEach((imageObj: any, index: number) => {
            if (index < 3) {
              let canvas: HTMLCanvasElement | null = null;
              if (index === 0) canvas = canvas1Ref.current;
              if (index === 1) canvas = canvas2Ref.current;
              if (index === 2) canvas = canvas3Ref.current;
              if (canvas) {
                const context = canvas.getContext('2d');
                const image = new Image();
                image.onload = function () {
                  context?.clearRect(0, 0, canvas!.width, canvas!.height);
                  context?.drawImage(image, 0, 0, canvas!.width, canvas!.height);
                };
                image.src = 'data:image/png;base64,' + imageObj.image;
              }
            }
          });
        }
      });
  };

  const getSelf = async () => {
    showLoadingOverlay()
    fetch(`${BACKEND_API_DOMAIN_NAME}/account/get-self`, {
      method: 'GET',
      credentials: "include"
    })
    .then((response) => response.json())
    .then((result) => {
      if(result.success)
      {
        setUser(result.user)
        setEmail(result.user[7])
        setFullName(result.user[8])
      }
      hideLoadingOverlay()
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
        pageNavigator("/")
      })
  };

  const onGetUserLogsClick = () => {
    showLoadingOverlay()
    console.log("Getting user logs from blockchain...");
    fetch(`${BACKEND_API_DOMAIN_NAME}/account/get-user-events`, {
      method: 'GET',
      credentials: "include"
    })
      .then((response) => response.json())
      .then((result) => {
        console.log(result)
        if(result.success == false)
        {
          setIsLoading(false)
          setServerResponseMessage(result.reason)
          handleScrollToSection("profile")
        }
        else
        {
          setLogs(result.logs)
          hideLoadingOverlay()
        }
      })
  };

  const handleScrollToSection = (id: 'profile' | 'password' | 'facereg' | 'delete' | 'activities') => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
      setActiveTab(id); // Set the active tab

      if (id == 'activities') {
        onGetUserLogsClick();
      }
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
    setShowPhotoUploadOverlay(false);
  };

  const setServerResponseMessage = (message: string) => {
    setIsLoading(false);
    setServerMessage(message);
  };

  const onSaveProfileClick = () => {
    showLoadingOverlay()
    fetch(`${BACKEND_API_DOMAIN_NAME}/account/update-profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: "include",
      body: JSON.stringify({ email: email, fullName: fullName }),
    })
    .then((response) => response.json())
    .then((result) => {
      setIsLoading(false)
      setServerResponseMessage(result.reason)
      if (result.success) {
        console.log("Profile info updated successfully.");
      } else {
        console.error("Error saving names:", result.reason);
      }
    });
  };

  const onUpdatePasswordClick = () => {
    showLoadingOverlay()

    if((currentPassword == "") || (newPassword == "") || (confirmNewPassword == "")) {
      setIsLoading(false);
      setServerResponseMessage("Password field cannot be blank!")
      return
    }

    if (newPassword != confirmNewPassword)
    {
      setIsLoading(false);
      setServerResponseMessage("New Password and confirm new password do not match!")
      return
    }

    if (currentPassword == newPassword)
    {
      setIsLoading(false);
      setServerResponseMessage("Password must be different!")
      return
    }

    fetch(`${BACKEND_API_DOMAIN_NAME}/account/update-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: "include",
      body: JSON.stringify({ password: newPassword }),
    })
    .then((response) => response.json())
    .then((result) => {
      setIsLoading(false)
      setServerResponseMessage(result.reason)
      if (result.success) {
        console.log("Profile info updated successfully.");
      } else {
        console.error("Error saving names:", result.reason);
      }
    });
  };

  const onConfirmNewFacePhotos = () => {
    showLoadingOverlay();
    fetch(`${BACKEND_API_DOMAIN_NAME}/account/update-face-hashes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: "include",
      body: JSON.stringify({
        faceArray: photoArray,
      }),
      
    })
      .then((response) => response.json())
      .then((result) => {
        setIsLoading(false);
        setServerResponseMessage(result.reason);
      });
  };

  const onDeleteSelfClick = () => {
    showLoadingOverlay();
    fetch(`${BACKEND_API_DOMAIN_NAME}/account/delete-self`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      credentials: "include"      
    })
      .then((response) => response.json())
      .then((result) => {
        setIsLoading(false);
        setServerResponseMessage(result.reason);
        if(result.success)
        {
          onLogOutClick();
        }
      });
  };

  useEffect(() => {
    checkSession();
    handleScrollToSection("profile");
    getSelf();
  }, []);

  const refreshPage = () => {
    window.location.reload();
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
            <a className="Home">Home</a>
          </Link>
          <Link to="/account">
            <a className="Account">Account Settings</a>
          </Link>
          <Link to="/permissions">
            <a className="logs">Groups & Permissions</a>
          </Link>
          <Link to="/about">
            <a className="About">About Us</a>
          </Link>
          <a onClick={onLogOutClick}>Log Out</a>
        </nav>
     </div>

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
                    <button onClick={hideLoadingOverlay} >OK</button>
                  </>
                )}
              </div>
            </div>
          )}

      {showPhotoUploadOverlay && (
            <div
              id="photoUploadOverlay"
              className="loading-overlay"
              style={{ display: 'flex' }}
            >
              <div className="loading-box">
                <h2 className='loading-box-title'>Capture Your Picture</h2>
                <p>
                  Your face is required for multifactor authentication.
                </p>
                <p>
                Please take three unique photos of yourself. 
                Photos should be clear with good lighting to improve system accuracy.
               </p>
                <div className="prompt-message-overlay">
                  {showFaceRecognitionMessage && (
                    <p
                      id="face_recognition_message"
                      className={
                        faceRecognitionSuccess
                          ? 'face_recognition_message_success'
                          : 'face_recognition_message_error'
                      }
                    >
                      {faceRecognitionMessage}
                    </p>
                  )}
                </div>
                {showCaptureContainer && (
                  <div id="capture-container">
                    <video
                      id="video"
                      width="320"
                      height="240"
                      autoPlay
                      ref={videoRef}
                    ></video>
                    <br />
                    <button onClick={capturePhoto}>Take Photo</button>
                  </div>
                )}
                {showPhotoContainer && (
                  <div id="photo-preview">
                    <h3 className='Preview-title'>Preview</h3>
                    <div className="photo-container">
                    <canvas
                      id="canvas1"
                      width="320"
                      height="240"
                      ref={canvas1Ref}
                    ></canvas>
                    <canvas
                      id="canvas2"
                      width="320"
                      height="240"
                      ref={canvas2Ref}
                    ></canvas>
                    <canvas
                      id="canvas3"
                      width="320"
                      height="240"
                      ref={canvas3Ref}
                    ></canvas>
                    </div>
                    <br />
                    <button id='uploadphoto-btn' onClick={uploadForRecognition}>Upload Photos</button>
                  </div>
                )}
                <div
                  id="final-photo-confirmation-container"
                  style={{
                    display: showFinalPhotoConfirmation ? 'block' : 'none',
                  }}
                >
                  <br />
                  <p>
                    Please check and verify that your face is clear and visible in
                    each photo.
                  </p>
                  <br />
                  <div className="capture-confirmation-buttons">
                    <button onClick={resetSignUpPhotos}>Start Over</button>
                    <button onClick={onConfirmNewFacePhotos}>Confirm New Face Photos</button>
                  </div>
                </div>
              </div>
            </div>)}

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
                        className={`activities ${activeTab === 'activities' ? 'active' : ''}`}
                        onClick={() => handleScrollToSection("activities")}
                    >
                    Activities
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
                      <label>Your Full Name:</label>
                      <input type="text" placeholder="John Doe" value={fullName} onChange={(e) => setFullName(e.target.value)}/>
                    </div>
                    <div className="profile-container">
                      <label>Your Email:</label>
                      <input type="text" placeholder="johndoe@organization.org" value={email} onChange={(e) => setEmail(e.target.value)}/>
                    </div>
                    <button className="profile-btn" onClick={onSaveProfileClick}>Submit Changes</button>
							    </section>

                  <section id="password" className="main">
                    <header className="major">
                      <h2>Change Password</h2>
                    </header>
                    <div className="password-container">
                      <input className="current-password-txt" type="password" placeholder="Current Password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} />
                      <input className="new-password-txt" type="password" placeholder="New Password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
                      <input className="confirm-password-txt" type="password" placeholder="Confirm New Password" value={confirmNewPassword} onChange={(e) => setConfirmNewPassword(e.target.value)} />
                    </div>
                    <br></br>
                    <button className="password-btn" onClick={onUpdatePasswordClick}>Submit</button>
              </section>

               <section id="facereg" className="main">
                    <header className="major">
                      <h2>Re-register Facial Recognition</h2>
                    </header>
                    <button className="facereg-btn" onClick={displayCapturePhotoOverlay}>Get Started!</button>
							</section> 

               <section id="activities" className="main">
                    <header className="major">
                      <h2>Account Activities</h2>
                    </header>
                    <div className="activities-table-container">
                    <table className="permissions-table">
                      <thead className="permissions-table-head">
                        <tr>
                          <th>Timestamp</th>
                          <th>Event</th>
                          <th>Data</th>
                          <th>Block</th>
                        </tr>
                      </thead>
                      <tbody>
                        {logs.map((log) => (
                          <tr key={log.timestamp}>
                            <td>{log.timestamp}</td>
                            <td>{log.event}</td>
                            <td>{log.data}</td>
                            <td>{log.block}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    </div>
                   
							</section>  

              <section id="delete" className="main">
               <header className="major">
                      <h2>Delete Your Account</h2>
                </header>
                <p>Are you sure you want to delete your account? This action cannot be undone.</p>
                    <br></br>
                    <button className="delete-btn" onClick={onDeleteSelfClick}>Delete Account</button>
              </section>
              
                            

              </div>
            </div>
        </div>

    </div>    
  );
};

export default account;
