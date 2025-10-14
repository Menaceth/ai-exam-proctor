import cv2
import mediapipe as mp

class GazeTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5
        )

        # Eye corner landmark indices from MediaPipe documentation
        self.LEFT_EYE = [33, 133]
        self.RIGHT_EYE = [362, 263]

    def check_gaze(self, frame):
        """Return True if student is looking away"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        looking_away = False

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            left_center_x = (landmarks[self.LEFT_EYE[0]].x + landmarks[self.LEFT_EYE[1]].x) / 2
            right_center_x = (landmarks[self.RIGHT_EYE[0]].x + landmarks[self.RIGHT_EYE[1]].x) / 2
            avg_x = (left_center_x + right_center_x) / 2

            # Simple threshold for attention
            if avg_x < 0.3 or avg_x > 0.7:
                looking_away = True
                cv2.putText(frame, "LOOKING AWAY!", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        return looking_away, frame
