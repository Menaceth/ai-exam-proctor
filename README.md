# AI Exam Proctor

An AI-powered online examination monitoring system that uses computer vision and deep learning to detect suspicious activities during online examinations. The system monitors candidates through their webcam and provides real-time updates through a web-based dashboard.

## Overview

The AI Exam Proctor aims to minimize malpractice in online examinations by automating the monitoring process. It uses facial detection, gaze monitoring, and object detection techniques to identify potentially suspicious activities.

The system consists of a Python-based backend that processes webcam frames and a web dashboard that displays monitoring results.

## Features

- **Face Detection:** Detects faces appearing in the webcam feed.
- **Looking Away Detection:** Monitors the candidate's face direction to identify when they look away from the screen.
- **Multiple Face Detection:** Identifies when more than one face appears in the camera frame.
- **Unauthorized Object Detection:** Detects potentially unauthorized objects such as mobile phones and books.
- **Real-Time Monitoring:** Continuously processes webcam frames and updates the dashboard.
- **Activity Logging:** Records suspicious activities with timestamps in CSV format.
- **Web Dashboard:** Displays live monitoring information in a centralized interface.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| OpenCV | Image processing and webcam frame handling |
| MediaPipe | Face detection and facial landmark detection |
| YOLOv8 | Object detection |
| PyTorch | Deep learning framework used by YOLOv8 |
| FastAPI | Backend development and API handling |
| Uvicorn | Runs the FastAPI application |
| NumPy | Numerical operations and image array processing |
| Pandas | Activity logging and CSV handling |
| HTML | Dashboard structure |
| CSS | Dashboard styling |
| JavaScript | Webcam access and frontend-backend communication |
| WebSocket | Real-time communication between frontend and backend |

## Project Structure

```text
ai_exam_proctor/
│
├── main.py
├── requirements.txt
├── .gitignore
│
├── templates/
│   └── index.html
│
├── static/
│   ├── script.js
│   └── style.css
│
├── logs/
│   └── activity_log.csv
│
└── README.md
```

*Note: The structure above represents the intended organization. Actual files may vary depending on the current implementation.*

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Menaceth/ai-exam-proctor.git
```

### 2. Navigate to the Project Directory

```bash
cd ai_exam_proctor
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

Start the FastAPI server using:

```bash
uvicorn main:app --reload
```

### 7. Open the Dashboard

Open your browser and navigate to:

```text
http://127.0.0.1:8000
```

Allow webcam access when prompted.

## System Requirements

- Windows 10 or later (recommended)
- Python 3.10 (recommended for MediaPipe compatibility)
- Minimum 8 GB RAM recommended
- Webcam (720p or higher recommended)
- Internet connection for initial dependency installation and YOLO model download

A dedicated GPU is optional. The system can also perform inference using the CPU, although performance may vary.

## Working

1. The candidate opens the examination dashboard.
2. The webcam captures live video frames.
3. The frontend sends the frames to the backend through WebSocket communication.
4. OpenCV and MediaPipe process the frames for facial analysis.
5. YOLOv8 identifies potentially unauthorized objects.
6. The backend generates monitoring results.
7. The dashboard displays the detection status in real time.
8. Suspicious activities can be recorded with timestamps for later review.

## Future Enhancements

- Face recognition for candidate identity verification.
- Improved gaze tracking and head pose estimation.
- Exam session authentication and management.
- Audio monitoring to identify suspicious background sounds.
- Detailed examination reports with suspicion scores.
- Database integration for storing candidate and examination records.
- Improved dashboard with analytics and historical activity reports.

## Limitations

- Detection accuracy depends on webcam quality, lighting conditions, and camera positioning.
- Object detection may produce false positives or miss certain objects.
- Looking-away detection requires further calibration for improved accuracy.
- The system currently focuses on local execution rather than cloud-based deployment.

## License

This project is currently developed for educational and academic purposes.

