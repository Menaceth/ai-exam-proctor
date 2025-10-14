let ws = null;
let isConnecting = false;
const video = document.getElementById("webcam-feed");
const connectionStatus = document.getElementById("connection-status");
const lastUpdate = document.getElementById("last-update");
const currentTimeElement = document.getElementById("current-time");
const currentUserElement = document.getElementById("current-user");

function updateCurrentTime() {
    const now = new Date();
    const formatted = now.toISOString().replace('T', ' ').split('.')[0];
    currentTimeElement.textContent = formatted;
}

function updateConnectionStatus(status, isConnected) {
    connectionStatus.textContent = status;
    connectionStatus.className = 'status-badge ' + (isConnected ? 'connected' : 'disconnected');
}

function connectWebSocket() {
    if (isConnecting) return;
    isConnecting = true;

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
    console.log("Connecting to WebSocket at:", wsUrl);

    try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log("WebSocket connected");
            updateConnectionStatus("Connected", true);
            isConnecting = false;
            startFrameCapture();
        };

        ws.onclose = () => {
            console.log("WebSocket disconnected");
            updateConnectionStatus("Disconnected", false);
            isConnecting = false;
            ws = null;
            setTimeout(connectWebSocket, 5000);
        };

        ws.onerror = (err) => {
            console.error("WebSocket error:", err);
            updateConnectionStatus("Error", false);
            isConnecting = false;
        };

        ws.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                console.log("Received data:", data);
                updateDashboard(data);
                updateLastUpdate();
            } catch (e) {
                console.error("Error parsing WebSocket message:", e);
            }
        };
    } catch (err) {
        console.error("Error creating WebSocket:", err);
        isConnecting = false;
        setTimeout(connectWebSocket, 5000);
    }
}

function updateLastUpdate() {
    const now = new Date();
    lastUpdate.textContent = now.toISOString().replace('T', ' ').split('.')[0];
}

function updateDashboard(data) {
    if (!data) {
        console.error("No data received");
        return;
    }

    const elements = {
        "faces-detected": {
            value: data.faces_detected ?? "0",
            alert: data.faces_detected === 0 || data.faces_detected > 1
        },
        "looking-away": {
            value: data.looking_away ? "Yes" : "No",
            alert: data.looking_away
        },
        "unauthorized-objects": {
            value: Array.isArray(data.unauthorized_objects) && data.unauthorized_objects.length > 0 
                ? data.unauthorized_objects.join(", ") 
                : "None",
            alert: Array.isArray(data.unauthorized_objects) && data.unauthorized_objects.length > 0
        },
        "multiple-faces": {
            value: data.multiple_faces ? "Yes" : "No",
            alert: data.multiple_faces
        }
    };

    for (const [id, info] of Object.entries(elements)) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = info.value;
            element.classList.toggle("alert", info.alert);
        }
    }
}

async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: 640,
                height: 480,
                frameRate: { ideal: 10, max: 15 }
            } 
        });
        video.srcObject = stream;
        await video.play();
        console.log("Webcam started successfully");
        return true;
    } catch (err) {
        console.error("Webcam error:", err);
        updateConnectionStatus("Webcam Error", false);
        return false;
    }
}

function startFrameCapture() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.log("WebSocket not ready, delaying frame capture");
        return;
    }

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");

    function captureAndSendFrame() {
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            return;
        }

        if (video.paused || video.ended) {
            return;
        }

        try {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const dataURL = canvas.toDataURL("image/jpeg", 0.7);
            ws.send(dataURL);
        } catch (err) {
            console.error("Error capturing/sending frame:", err);
        }
    }

    setInterval(captureAndSendFrame, 200);
}

// Initialize everything when the page loads
window.addEventListener('DOMContentLoaded', async () => {
    console.log("Page loaded, initializing...");
    
    // Set current user
    currentUserElement.textContent = "Menaceth";
    
    // Start time updates
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    
    // Start webcam and WebSocket
    const webcamStarted = await startWebcam();
    if (webcamStarted) {
        connectWebSocket();
    }
});