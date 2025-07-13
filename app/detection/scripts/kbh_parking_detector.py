import cv2
import pickle
import numpy as np
import sys
import os
import argparse
import time

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from app.utils.notifier import send_slot_update

# Argument parser for --stream flag
parser = argparse.ArgumentParser()
parser.add_argument('--stream', action='store_true', help='Enable MJPEG streaming to stdout')
args = parser.parse_args()

# --- Config ---
PARKING_ID = "68700289a320c9d36bd397a4"

# Video feed
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
video_path = os.path.join(BASE_DIR, 'kbh_parking_video.mp4')
positions_path = os.path.join(BASE_DIR, 'kbh_parking_positions')

cap = cv2.VideoCapture(video_path)

with open(positions_path, 'rb') as f:
    posList = pickle.load(f)

prev_parking_status = [False] * len(posList)
width, height = 200, 200

# --- FPS Safe Defaults ---
fps = cap.get(cv2.CAP_PROP_FPS)
fps = fps if fps > 0 else 25

# Use appropriate frame rate for streaming
if args.stream:
    fps = min(fps * 1.2, 30)  # Slightly increase fps for streaming, max 30 fps
def rescaleframe(frame, scale=0.5):
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height)
    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)

def checkParkingSpace(imgPro):
    global prev_parking_status
    parking_status = []
    spaceCounter = 0

    for pos in posList:
        x, y = pos

        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)

        if count < 4500:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
            occupied = False # parking space is free
        else:
            color = (0, 0, 255)
            thickness = 2
            occupied = True # parking space is occupied
        # Optionally draw rectangles or overlays here if needed

        parking_status.append(occupied)

    # Check for changes in parking space statuses
    if parking_status != prev_parking_status:
        prev_parking_status = parking_status
        send_slot_update(PARKING_ID, spaceCounter)
        print(f"[INFO] Free slots: {spaceCounter}", flush=True)

# --- Main Loop ---
while True:
    start_time = time.time()
    success, img = cap.read()
    if not success:
        break

    img_r = rescaleframe(img)
    imgGray = cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    checkParkingSpace(imgDilate)

    if args.stream:
        # Encode frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', img_r)
        if not ret:
            continue

        # Proper MJPEG boundary format for streaming
        frame_data = (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n'
            b'Content-Length: ' + str(len(jpeg.tobytes())).encode() + b'\r\n\r\n' +
            jpeg.tobytes() + b'\r\n'
        )
        
        sys.stdout.buffer.write(frame_data)
        sys.stdout.buffer.flush()

    # Timing
    elapsed = time.time() - start_time
    if args.stream:
        # Comfortable frame rate for streaming
        delay = max(0.02, 1.0 / fps - elapsed)  # Minimum 20ms delay for smoother viewing
    else:
        # Normal frame rate for detection only
        delay = max(0.005, 1.0 / fps - elapsed)
    time.sleep(delay)