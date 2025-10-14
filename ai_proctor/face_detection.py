import cv2
import mediapipe as mp

class FaceDetector:
    def __init__(self, min_detection_confidence=0.5):
        self.mp_face = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.detector = self.mp_face.FaceDetection(
            model_selection=1, min_detection_confidence=min_detection_confidence
        )

    def detect_faces(self, frame):
        """Detect faces in a frame and draw bounding boxes"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.detector.process(rgb_frame)
        faces_detected = 0

        if results.detections:
            faces_detected = len(results.detections)
            for detection in results.detections:
                self.mp_drawing.draw_detection(frame, detection)

        return faces_detected, frame
