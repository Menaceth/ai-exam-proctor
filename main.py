import os
import csv
import datetime
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import base64
import cv2
import numpy as np
import mediapipe as mp
from ultralytics import YOLO
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_exam_logging():
    log_file = Path('logs/exam-log.csv')
    log_file.parent.mkdir(exist_ok=True)
    
    if not log_file.exists():
        with open(log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Timestamp', 
                'User', 
                'Event Type', 
                'Faces Detected',
                'Looking Away',
                'Multiple Faces',
                'Unauthorized Objects'
            ])
    return log_file

def log_exam_event(log_file, user, event_data):
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp,
            user,
            'frame_analysis',
            event_data.get('faces_detected', 0),
            event_data.get('looking_away', False),
            event_data.get('multiple_faces', False),
            ','.join(event_data.get('unauthorized_objects', [])) or 'None'
        ])

app = FastAPI()

# Set up logging file
log_file = setup_exam_logging()

# Check if static directory exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    logger.error(f"Static directory not found: {static_dir}")
    os.makedirs(static_dir)
    logger.info(f"Created static directory: {static_dir}")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
logger.info(f"Mounted static files from: {static_dir}")

# MediaPipe Face Detection
mp_face = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh

face_detector = mp_face.FaceDetection(min_detection_confidence=0.5)
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5)

# Load YOLO model
try:
    yolo_model = YOLO("yolov8n.pt")
    logger.info("YOLO model loaded successfully")
except Exception as e:
    logger.error(f"Error loading YOLO model: {str(e)}")
    raise

UNAUTHORIZED_CLASSES = ["cell phone", "book", "laptop"]

def decode_image(base64_string):
    try:
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        img_bytes = base64.b64decode(base64_string)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Failed to decode image")
        return frame
    except Exception as e:
        logger.error(f"Error decoding image: {str(e)}")
        raise

def detect_faces(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_detector.process(rgb_frame)
    if results.detections:
        return len(results.detections), results.detections
    return 0, []

def detect_looking_away(frame, face_detections):
    if len(face_detections) == 0:
        return True
    h, w, _ = frame.shape
    face = face_detections[0]
    bbox = face.location_data.relative_bounding_box
    x_center = (bbox.xmin + bbox.width / 2) * w
    return x_center < w*0.2 or x_center > w*0.8

def detect_unauthorized_objects(frame):
    results = yolo_model.predict(frame)
    objects_detected = []
    for result in results:
        for box, cls_id, conf in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf):
            cls_name = yolo_model.names[int(cls_id)]
            if cls_name in UNAUTHORIZED_CLASSES:
                objects_detected.append(cls_name)
    return objects_detected

def detect_multiple_faces(num_faces):
    return num_faces > 1

def get_exam_statistics(log_file):
    statistics = {
        'total_frames': 0,
        'violations': {
            'looking_away': 0,
            'multiple_faces': 0,
            'unauthorized_objects': 0,
            'no_face': 0
        },
        'unauthorized_objects_detected': {}
    }
    
    with open(log_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            statistics['total_frames'] += 1
            
            if row['Looking Away'] == 'True':
                statistics['violations']['looking_away'] += 1
            
            if row['Multiple Faces'] == 'True':
                statistics['violations']['multiple_faces'] += 1
            
            if row['Faces Detected'] == '0':
                statistics['violations']['no_face'] += 1
            
            objects = row['Unauthorized Objects']
            if objects and objects != 'None':
                statistics['violations']['unauthorized_objects'] += 1
                for obj in objects.split(','):
                    statistics['unauthorized_objects_detected'][obj] = \
                        statistics['unauthorized_objects_detected'].get(obj, 0) + 1
    
    return statistics

@app.get("/")
async def get():
    try:
        with open("templates/index.html") as f:
            content = f.read()
            logger.info("Successfully loaded index.html")
            return HTMLResponse(content)
    except FileNotFoundError as e:
        logger.error(f"Failed to load index.html: {e}")
        raise HTTPException(status_code=404, detail="Template not found")

@app.get("/statistics")
async def get_statistics():
    return get_exam_statistics(log_file)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        logger.info("WebSocket client connected")
        
        while True:
            try:
                data = await websocket.receive_text()
                frame = decode_image(data)
                
                num_faces, face_detections = detect_faces(frame)
                looking_away = detect_looking_away(frame, face_detections)
                unauthorized_objects = detect_unauthorized_objects(frame)
                multiple_faces = detect_multiple_faces(num_faces)

                result = {
                    "faces_detected": num_faces,
                    "looking_away": looking_away,
                    "unauthorized_objects": unauthorized_objects,
                    "multiple_faces": multiple_faces
                }
                
                # Log the event
                log_exam_event(log_file, "Menaceth", result)
                
                await websocket.send_json(result)
                logger.debug(f"Sent result: {result}")

            except Exception as e:
                error_msg = f"Error processing frame: {str(e)}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                try:
                    error_result = {
                        "error": error_msg,
                        "faces_detected": 0,
                        "looking_away": False,
                        "unauthorized_objects": [],
                        "multiple_faces": False
                    }
                    # Log the error event
                    log_exam_event(log_file, "Menaceth", error_result)
                    await websocket.send_json(error_result)
                except:
                    break

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}\n{traceback.format_exc()}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)