import cv2

cam = cv2.VideoCapture(0)  # Use 0 for the default webcam
if not cam.isOpened():
    print("Error: Could not open webcam")
else:
    print("Webcam opened successfully!")

while True:
    ret, frame = cam.read()
    if not ret:
        print("Failed to capture image")
        break
    
    cv2.imshow("Webcam Test", frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to exit
        break

cam.release()
cv2.destroyAllWindows()
