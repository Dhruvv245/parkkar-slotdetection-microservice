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
PARKING_ID = "5c88fa8cf4afda39709c2970"

# Video feed
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
video_path = os.path.join(BASE_DIR, 'chemvid.mp4')
positions_path = os.path.join(BASE_DIR, 'chemposn')

# Video feed
cap = cv2.VideoCapture(video_path)

with open(positions_path, 'rb') as f:
    posList = pickle.load(f)

prev_parking_status = [False] * len(posList)
width, height = 150, 197

# --- FPS Safe Defaults ---
fps = cap.get(cv2.CAP_PROP_FPS)
fps = fps if fps > 0 else 25

def checkParkingSpace(imgPro):
    global prev_parking_status
    parking_status = []
    spaceCounter = 0

    for pos in posList:
        x, y = pos
        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)

        if count < 2000:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
            occupied = False
        else:
            color = (0, 0, 255)
            thickness = 2
            occupied = True
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
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

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    checkParkingSpace(imgDilate)

    if args.stream:
        # Encode frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', img)
        if not ret:
            continue

        # Write MJPEG frame to stdout
        sys.stdout.buffer.write(b'--frame\r\n')
        sys.stdout.buffer.write(b'Content-Type: image/jpeg\r\n\r\n')
        sys.stdout.buffer.write(jpeg.tobytes())
        sys.stdout.buffer.write(b'\r\n')
        sys.stdout.flush()

    # Timing
    elapsed = time.time() - start_time
    delay = max(0.005, 1.0 / fps - elapsed)
    time.sleep(delay)