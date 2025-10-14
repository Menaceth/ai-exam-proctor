import cv2
import requests
import numpy as np

# Backend URL
url = "http://127.0.0.1:8000/analyze-frame"

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Encode frame as JPEG
        _, img_encoded = cv2.imencode('.jpg', frame)

        # Send frame to backend
        try:
            response = requests.post(url, files={"file": img_encoded.tobytes()})
            data = response.json()
            faces_detected = data.get('faces_detected', 0)
            looking_away = data.get('looking_away', False)
            unauthorized_objects = data.get('unauthorized_objects', False)
        except Exception as e:
            print("Error sending frame:", e)
            faces_detected = 0
            looking_away = False
            unauthorized_objects = False

        # Terminal print
        print(f"Faces: {faces_detected}, Looking Away: {looking_away}, Unauthorized Objects: {unauthorized_objects}")

        # Color coding: red if any alert, green if all good
        color = (0, 255, 0)  # Green default
        if looking_away or unauthorized_objects:
            color = (0, 0, 255)  # Red alert

        # Display info on webcam
        cv2.putText(frame,
                    f"Faces: {faces_detected} | Looking Away: {looking_away} | Objects: {unauthorized_objects}",
                    (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Show webcam
        cv2.imshow("AI Exam Proctor - Press 'q' to quit", frame)

        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
