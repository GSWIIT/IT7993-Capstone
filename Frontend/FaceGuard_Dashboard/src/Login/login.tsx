import React, { useRef, useState } from 'react';
import './login.css';
const LoginPage: React.FC = () => {
  // Refs for webcam and canvas elements
  const videoRef = useRef<HTMLVideoElement>(null!);
  const canvas1Ref = useRef<HTMLCanvasElement>(null!);
  const canvas2Ref = useRef<HTMLCanvasElement>(null!);
  const canvas3Ref = useRef<HTMLCanvasElement>(null!);
  const video2FARef = useRef<HTMLVideoElement>(null!);
  const canvas2FARef = useRef<HTMLCanvasElement>(null!);

  // State for overlays and messages
  const [showLoadingOverlay, setShowLoadingOverlay] = useState(false);
  const [showLoadingGraphics, setShowLoadingGraphics] = useState(false);
  const [showLoadingPromptOverlay, setShowLoadingPromptOverlay] = useState(false);
  const [loadingPromptMessage, setLoadingPromptMessage] = useState('');
  const [loadingPromptSuccess, setLoadingPromptSuccess] = useState(false);
  const [loginMessage, setLoginMessage] = useState('');
  const [showLoginMessage, setShowLoginMessage] = useState(false);
  const [signupMessage, setSignupMessage] = useState('');
  const [showSignupMessage, setShowSignupMessage] = useState(false);
  const [twoFAErrorMessage, setTwoFAErrorMessage] = useState('');
  const [faceRecognitionMessage, setFaceRecognitionMessage] = useState('');
  const [faceRecognitionSuccess, setFaceRecognitionSuccess] = useState(false);
  const [showFaceRecognitionMessage, setShowFaceRecognitionMessage] = useState(false);

  // State for login/signup and webcam/photo capture
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [signupUsername, setSignupUsername] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [signupPasswordConfirm, setSignupPasswordConfirm] = useState('');
  const [isInitialSignup, setIsInitialSignup] = useState(true);
  const [signUpButtonDisabled, setSignUpButtonDisabled] = useState(false);
  const [photosTaken, setPhotosTaken] = useState(0);
  const [photoArray, setPhotoArray] = useState<string[]>([]);
  const [confirmedUniqueUsername, setConfirmedUniqueUsername] = useState(false);
  const [confirmedPhotos, setConfirmedPhotos] = useState(false);

  // State to control overlay display sections
  const [showCaptureContainer, setShowCaptureContainer] = useState(true);
  const [showPhotoContainer, setShowPhotoContainer] = useState(false);
  const [showFinalPhotoConfirmation, setShowFinalPhotoConfirmation] = useState(false);
  const [showPhotoUploadOverlay, setShowPhotoUploadOverlay] = useState(false);
  const [showLoginFaceAuthOverlay, setShowLoginFaceAuthOverlay] = useState(false);

  // ----- Helper functions -----
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

    fetch('http://127.0.0.1:5000/auth/checkface', {
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

  const displayCapturePhotoOverlay = () => {
    setShowLoadingOverlay(false);
    setShowLoadingPromptOverlay(false);
    setShowLoadingGraphics(false);
    setShowFinalPhotoConfirmation(false);
    setShowFaceRecognitionMessage(false);
    setShowCaptureContainer(true);
    setShowPhotoContainer(false);
    setShowPhotoUploadOverlay(true);
    startWebcamCapture();
  };

  const displayLoadingOverlay = () => {
    setShowLoadingPromptOverlay(false);
    setShowLoadingOverlay(true);
    setShowLoadingGraphics(true);
  };

  const displayLoadingPrompt = (message: string, success: boolean) => {
    setShowLoadingOverlay(true);
    setShowLoadingGraphics(false);
    setLoadingPromptMessage(message);
    setLoadingPromptSuccess(success);
    setShowLoadingPromptOverlay(true);
  };

  const closeLoadingPrompt = () => {
    setShowLoadingOverlay(false);
    setShowLoadingPromptOverlay(false);
  };

  const close2FAFaceOverlay = () => {
    setShowLoginFaceAuthOverlay(false);
  };

  const showLoginMessageFunc = (message: string) => {
    setLoginMessage(message);
    setShowLoginMessage(true);
  };

  const showSignupMessageFunc = (message: string) => {
    setSignupMessage(message);
    setShowSignupMessage(true);
  };

  const onSignInClick = () => {
    if (loginUsername.trim() === '') {
      showLoginMessageFunc('Error: Username cannot be blank.');
      return;
    }
    if (loginPassword.trim() === '') {
      showLoginMessageFunc('Error: Password cannot be blank.');
      return;
    }
    displayLoadingOverlay();
    fetch('http://127.0.0.1:5000/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: loginUsername, password: loginPassword }),
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.success) {
          capture2FAFrames();
        } else {
          displayLoadingPrompt(result.reason, result.success);
        }
      });
  };

  const capture2FAFrames = () => {
    setShowLoginFaceAuthOverlay(true);

    const videoCheckInterval = setInterval(() => {
      if (video2FARef.current) {
        clearInterval(videoCheckInterval); // Stop checking once the element is available
        navigator.mediaDevices
          .getUserMedia({ video: true })
          .then((stream) => {
            video2FARef.current!.srcObject = stream;
          })
          .catch((err) => {
            console.error('Error accessing webcam: ', err);
            alert('Unable to access webcam.');
          });
      }
    }, 100); // Check every 100ms

    const frameCount = 5;
    const interval = 400;
    let count = 0;
    const frames: string[] = [];
    const captureInterval = setInterval(() => {
      if (canvas2FARef.current && video2FARef.current) {
        const context = canvas2FARef.current.getContext('2d');
        context?.drawImage(video2FARef.current, 0, 0, 320, 240);
        const imageData = canvas2FARef.current
          .toDataURL('image/png')
          .split(',')[1];
        frames.push(imageData);
      }
      count++;
      if (count >= frameCount) {
        clearInterval(captureInterval);
        fetch('http://127.0.0.1:5000/auth/login-2FA-Face', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: loginUsername,
            password: loginPassword,
            frames: frames,
          }),
        })
          .then((response) => response.json())
          .then((result) => {
            console.log(result)
            if (result.success) {
              close2FAFaceOverlay();
              displayLoadingPrompt(
                'Face detected! Two Factor authentication successful.',
                true
              );
              localStorage.setItem("session", result.session); // Store username locally
              window.location.href = '/home';
            } else {
              setTwoFAErrorMessage(result.reason);
              setTimeout(capture2FAFrames, 50);
            }
          })
          .catch((error) => console.error('Error:', error));
      }
    }, interval);
  };

  const onPreSignUpClick = () => {
    setIsInitialSignup(false);
  };

  const onSignUpClick = async () => {
    setSignUpButtonDisabled(true);
    setShowPhotoUploadOverlay(false);
    if (signupUsername.trim() === '') {
      showSignupMessageFunc('Error: Username cannot be blank.');
      return;
    }
    if (signupPassword.trim() === '') {
      showSignupMessageFunc('Error: Password cannot be blank.');
      return;
    }
    if (signupPassword !== signupPasswordConfirm) {
      showSignupMessageFunc('Error: Passwords do not match.');
      return;
    }
    if (!confirmedUniqueUsername) {
      displayLoadingOverlay();
      const usernameResponse = await fetch('http://127.0.0.1:5000/auth/usernamecheck', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: signupUsername }),
      });
      const result = await usernameResponse.json();
      setConfirmedUniqueUsername(result.success);
      if (!result.success) {
        displayLoadingPrompt(result.reason, result.success);
        return;
      }
    }
    if (!confirmedPhotos) {
      displayCapturePhotoOverlay();
      return;
    }
    displayLoadingOverlay();
    fetch('http://127.0.0.1:5000/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: signupUsername,
        password: signupPassword,
        faceArray: photoArray,
      }),
    })
      .then((response) => response.json())
      .then((result) => {
        displayLoadingPrompt(result.reason, result.success);
      });
  };
  

  // ----------------- JSX -----------------
  return (
    <>
      {/* Link to external stylesheet */}
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
            {isInitialSignup ? (
              <div id="initial_signup_div" style={{ display: 'block' }}>
                <h2 className="white_text">New User?</h2>
                <p className="medium_padding white_text">
                  No worries! Click the button below to create a free account
                  with us.
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
                  <input
                    type="text"
                    className="white_outline"
                    id="signup_username"
                    placeholder="Your New Username"
                    name="username"
                    value={signupUsername}
                    onChange={(e) => setSignupUsername(e.target.value)}
                  />
                </div>
                <div className="small_padding">
                  <input
                    type="password"
                    className="white_outline"
                    id="signup_password"
                    placeholder="Your Password"
                    name="password"
                    value={signupPassword}
                    onChange={(e) => setSignupPassword(e.target.value)}
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
                    onChange={(e) =>
                      setSignupPasswordConfirm(e.target.value)
                    }
                  />
                </div>
                <div className="small_padding">
                  <button
                    id="signUpButton"
                    onClick={onSignUpClick}
                    disabled={signUpButtonDisabled}
                  >
                    Sign Up
                  </button>
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
              <div id="loadingGraphics" style={{ display: 'block' }}>
                <img
                  src="/src/assets/ethereum.png"
                  alt="Ethereum Logo"
                  className="loading-image"
                />
                <div className="spinner"></div>
                <p>
                  Communicating with BlockChain, please wait... (this may take a
                  minute)...
                </p>
              </div>
            )}
            {showLoadingPromptOverlay && (
              <div id="loadingPromptOverlay" style={{ display: 'block' }}>
                <img
                  id="loadingPromptImage"
                  src={
                    loadingPromptSuccess
                      ? '/src/assets/ethereum.png'
                      : '/src/assets/error icon.png'
                  }
                  alt="Prompt"
                  className="error-image"
                />
                <p
                  id="loadingPromptMessage"
                  className={
                    loadingPromptSuccess
                      ? 'login_prompt_success'
                      : 'login_prompt_error'
                  }
                >
                  {loadingPromptMessage}
                </p>
                <button onClick={closeLoadingPrompt}>Ok</button>
              </div>
            )}
          </div>
        </div>
      )}

      {showLoginFaceAuthOverlay && (
        <div
          id="loginFaceAuthOverlay"
          className="loading-overlay"
          style={{ display: 'flex' }}
        >
          <div className="loading-box">
            <h2>Scan Face for Authentication</h2>
            <br />
            <p>Please wait while we scan your face for authentication...</p>
            <br />
            <video
              id="2FA_video"
              width="320"
              height="240"
              autoPlay
              ref={video2FARef}
            ></video>
            <br />
            <div className="two_factor_capture_container">
              <canvas
                id="2FA-capture"
                width="320"
                height="240"
                ref={canvas2FARef}
              ></canvas>
            </div>
            <br />
            <div className="prompt-message-overlay">
              {twoFAErrorMessage && (
                <p id="2FAErrorMessage" className="login_prompt_error">
                  {twoFAErrorMessage}
                </p>
              )}
            </div>
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
            <h2>Capture Your Picture</h2>
            <p>
              Your face is required for multifactor authentication.
            </p>
            <p>
              Please take three unique photos of yourself. Photos should be
              clear with good lighting to improve system accuracy.
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
                <h3>Preview</h3>
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
                <button onClick={uploadForRecognition}>Upload Photos</button>
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
              <button onClick={resetSignUpPhotos}>Start Over</button>
              <button onClick={onSignUpClick}>Finish Sign Up</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default LoginPage;
