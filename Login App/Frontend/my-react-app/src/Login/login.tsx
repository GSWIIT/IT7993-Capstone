// Login.tsx
import React, { useState, useRef, useEffect } from 'react';
import './login.css';

const Login: React.FC = () => {
  // Login/Signup form state
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [signupUsername, setSignupUsername] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [signupPasswordConfirm, setSignupPasswordConfirm] = useState('');
  const [loginMessage, setLoginMessage] = useState('');
  const [showLoginMessage, setShowLoginMessage] = useState(false);
  const [signupMessage, setSignupMessage] = useState('');
  const [showSignupMessage, setShowSignupMessage] = useState(false);
  const [isSignUpMode, setIsSignUpMode] = useState(false);

  // Overlays and prompts
  const [showLoadingOverlay, setShowLoadingOverlay] = useState(false);
  const [showLoadingPromptOverlay, setShowLoadingPromptOverlay] = useState(false);
  const [showLoadingGraphics, setShowLoadingGraphics] = useState(false);
  const [showPhotoUploadOverlay, setShowPhotoUploadOverlay] = useState(false);
  const [loadingPromptMessage, setLoadingPromptMessage] = useState('');
  const [loadingPromptSuccess, setLoadingPromptSuccess] = useState<boolean | null>(null);

  // Refs for webcam and canvas
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // Using refs for the captured images (won't cause re-renders)
  const base64Image1Ref = useRef<string | null>(null);
  const base64Image2Ref = useRef<string | null>(null);

  //Start webcam capture
  const startWebcamCapture = () => {
    if (videoRef.current) {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            videoRef.current.play();
          }
        })
        .catch((err) => {
          console.error('Error accessing webcam: ', err);
          alert('Unable to access webcam.');
        });
    }
  };

  // Ensure the webcam starts when the component mounts
  useEffect(() => {
    startWebcamCapture();
  }, []);

// useEffect(() => {
//     // Request camera access when the component mounts
//     const startWebcamCapture = async () => {
//       try {
//         const stream = await navigator.mediaDevices.getUserMedia({ video: true });
//         if (videoRef.current) {
//           videoRef.current.srcObject = stream;
//           videoRef.current.play();
//         }
//       } catch (error) {
//         console.error('Error accessing the camera', error);
//       }
//     };

//     startWebcamCapture();

//     // Cleanup: stop all video tracks when the component unmounts
//     return () => {
//       if (videoRef.current?.srcObject) {
//         const stream = videoRef.current.srcObject as MediaStream;
//         stream.getTracks().forEach(track => track.stop());
//       }
//     };
//   }, []);

  // Capture a photo from the video stream
  const capturePhoto = () => {
    if (canvasRef.current && videoRef.current) {
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      if (context) {
        context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      }
    }
  };

  // Upload captured photo(s) for face recognition
  const uploadForRecognition = () => {
    if (canvasRef.current) {
      if (base64Image1Ref.current === null) {
        base64Image1Ref.current = canvasRef.current
          .toDataURL('image/png')
          .split(',')[1];
        return;
      }
      if (base64Image2Ref.current === null) {
        base64Image2Ref.current = canvasRef.current
          .toDataURL('image/png')
          .split(',')[1];
      }

      fetch('/api/run_face_recognition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          facePNG1: base64Image1Ref.current,
          facePNG2: base64Image2Ref.current,
        }),
      })
        .then((response) => response.json())
        .then((result) => {
          displayLoadingPrompt(result.reason, result.success);
          if (result.image) {
            const img = new Image();
            img.onload = () => {
              if (canvasRef.current) {
                canvasRef.current.width = img.width;
                canvasRef.current.height = img.height;
                const context = canvasRef.current.getContext('2d');
                if (context) {
                  context.drawImage(img, 0, 0, img.width, img.height);
                }
              }
            };
            img.src = 'data:image/png;base64,' + result.image;
          }

          if (result.hamming_distance <= 5) {
            displayLoadingPrompt(
              'Hamming Distance: ' +
                result.hamming_distance +
                '. Similarity check passed!',
              true
            );
          } else {
            displayLoadingPrompt(
              'Hamming Distance: ' +
                result.hamming_distance +
                '. Similarity check failed! Please try again.',
              false
            );
          }
        });
    }
  };

  // Overlay display functions
  const displayCapturePhotoOverlay = () => {
    setShowLoadingOverlay(true);
    setShowLoadingPromptOverlay(false);
    setShowLoadingGraphics(false);
    setShowPhotoUploadOverlay(true);
    startWebcamCapture();
  };

  const displayLoadingOverlay = () => {
    setShowLoadingPromptOverlay(false);
    setShowLoadingOverlay(true);
    setShowLoadingGraphics(true);
  };

  const displayLoadingPrompt = (message: string, success: boolean) => {
    setShowLoadingGraphics(false);
    setLoadingPromptMessage(message);
    setLoadingPromptSuccess(success);
    setShowLoadingPromptOverlay(true);
  };

  const closeLoadingPrompt = () => {
    setShowLoadingOverlay(false);
  };

  // Message display functions for login/signup
  const showLoginMsg = (message: string) => {
    setLoginMessage(message);
    setShowLoginMessage(true);
  };

  const showSignupMsg = (message: string) => {
    setSignupMessage(message);
    setShowSignupMessage(true);
  };

  // Login button click handler
  const onSignInClick = async () => {
    if (loginUsername.trim() === '') {
      showLoginMsg('Error: Username cannot be blank.');
      return;
    }
    if (loginPassword.trim() === '') {
      showLoginMsg('Error: Password cannot be blank.');
      return;
    }
    displayLoadingOverlay();
    const response = await fetch("{{url_for('login.login')}}", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: loginUsername, password: loginPassword }),
    });
    const result = await response.json();
    displayLoadingPrompt(result.reason, result.success);
  };

  // Switch to sign-up form
  const onPreSignUpClick = () => {
    setIsSignUpMode(true);
  };

  // Sign-up button click handler
  const onSignUpClick = async () => {
    if (signupUsername.trim() === '') {
      showSignupMsg('Error: Username cannot be blank.');
      return;
    }
    if (signupPassword.trim() === '') {
      showSignupMsg('Error: Password cannot be blank.');
      return;
    }
    if (signupPassword !== signupPasswordConfirm) {
      showSignupMsg('Error: Passwords do not match.');
      return;
    }
    displayLoadingOverlay();
    const response = await fetch('/api/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: signupUsername, password: signupPassword }),
    });
    const result = await response.json();
    displayLoadingPrompt(result.reason, result.success);
  };

  return (
    <div>
      <button onClick={displayCapturePhotoOverlay}>Get Face Data</button>

      <div className="login_signup_container">
        <div className="login_signup_column_left">
          <div className="login_signup_center_left">
            <div>
              <h2 className="small_padding">Sign In</h2>
              {showLoginMessage && (
                <div id="loginMessageDiv" className="small_padding">
                  <p id="loginMessage" className="error_message">
                    {loginMessage}
                  </p>
                </div>
              )}
              <div>
                <div className="small_padding">
                  <input
                    type="text"
                    id="login_username"
                    placeholder="Username"
                    value={loginUsername}
                    onChange={(e) => setLoginUsername(e.target.value)}
                  />
                </div>
                <div className="small_padding">
                  <input
                    type="password"
                    id="login_password"
                    placeholder="Password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                  />
                </div>
              </div>
              <br />
              <button onClick={onSignInClick}>Sign In</button>
            </div>
          </div>
        </div>
        <div className="login_signup_column_right">
          <div className="login_signup_center_right">
            {!isSignUpMode ? (
              <div id="initial_signup_div" style={{ display: 'block' }}>
                <h2 className="white_text">New User?</h2>
                <p className="medium_padding white_text">
                  No worries! Click the button below to create a free account with
                  us.
                </p>
                <button onClick={onPreSignUpClick}>Sign Up</button>
              </div>
            ) : (
              <div id="registration_signup_div" style={{ display: 'block' }}>
                <h2 className="small_padding white_text">Create Account</h2>
                {showSignupMessage && (
                  <div id="signupMessageDiv" className="small_padding">
                    <p id="signupMessage" className="error_message">
                      {signupMessage}
                    </p>
                  </div>
                )}
                <div className="small_padding">
                  <input type="text" className="white_outline" id="signup_username"
                    placeholder="Your New Username" name="username" value={signupUsername}
                    onChange={(e) => setSignupUsername(e.target.value)}
                  />
                </div>
                <div className="small_padding">
                  <input  type="password" className="white_outline" id="signup_password" placeholder="Your Password"
                    name="password" value={signupPassword} onChange={(e) => setSignupPassword(e.target.value)}
                  />
                </div>
                <div className="small_padding">
                  <input
                    type="password"
                    className="white_outline"
                    id="signup_password_confirm"
                    placeholder="Confirm Password"
                    name="password_confirm"
                    value={signupPasswordConfirm}
                    onChange={(e) => setSignupPasswordConfirm(e.target.value)}
                  />
                </div>
                <div className="small_padding">
                  <button onClick={onSignUpClick}>Sign Up</button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {showLoadingOverlay && (
        <div
          id="loadingOverlay"
          className="loading-overlay"
          style={{ display: 'flex' }}
        >
          <div className="loading-box">
            {showLoadingGraphics && (
              <div id="loadingGraphics">
                <img
                  src="/src/assets/ethereum.png"
                  alt="Ethereum Logo"
                  className="loading-image"
                />
                <div className="spinner"></div>
                <p>Please wait (this may take a minute)...</p>
              </div>
            )}
            {showLoadingPromptOverlay && (
              <div id="loadingPromptOverlay">
                <img id="loadingPromptImage"
                  src={
                    loadingPromptSuccess
                      ? '/static/ethereum.png'
                      : '/static/error icon.png'
                  }
                  alt="Status"
                  className={
                    loadingPromptSuccess
                      ? 'login_prompt_success'
                      : 'login_prompt_error'
                  }
                />
                <p id="loadingPromptMessage" className="login_prompt_text">
                  {loadingPromptMessage}
                </p>
                <button onClick={closeLoadingPrompt}>Ok</button>
              </div>
            )}
            {showPhotoUploadOverlay && (
              <div id="photoUploadOverlay">
                <h2>Capture Your Picture</h2>
                <p>
                  Your face is needed for multifactor authentication. Please take a
                  picture of yourself to continue.
                </p>

                <video id="video" width="320" height="240" autoPlay ref={videoRef} />
                <br />
                <button id="capture" onClick={capturePhoto}>Take Photo</button>

                <div id="photo-container">
                  <h3>Preview</h3>
                  <canvas id="canvas" width="320" height="240" ref={canvasRef} />
                  <br />
                  <button id="upload" onClick={uploadForRecognition}>Upload Photo</button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Login;
