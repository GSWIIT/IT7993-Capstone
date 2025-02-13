import cv2

def capture_face():
    """Captures the user's face using OpenCV."""
    cam = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    print("Capturing face. Look at the camera...")
    while True:
        ret, frame = cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            cv2.imshow("Face Capture", face)
            cv2.waitKey(30000)  # Capture after 2 seconds
            cam.release()
            cv2.destroyAllWindows()
            return face

    cam.release()
    cv2.destroyAllWindows()
    return None

capture_face()