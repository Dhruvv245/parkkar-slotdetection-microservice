import cv2
import pickle
import cvzone
import numpy as np
import sys
import os   
import argparse
import time

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from app.utils.notifier import send_slot_update

# Argument parser for --stream flag
parser = argparse.ArgumentParser()
parser.add_argument('--stream', action='store_true', help='Enable MJPEG streaming to stdout')
args = parser.parse_args()

# --- Config ---
PARKING_ID = "661661e96104b67c07d092ec"

# Video feed
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
video_path = os.path.join(BASE_DIR, 'workshop_parking_video.mp4')
positions_path = os.path.join(BASE_DIR, 'workshop_parking_positions')
cap = cv2.VideoCapture(video_path)

with open(positions_path, 'rb') as f:
    posList = pickle.load(f)

prev_parking_status = [False] * len(posList)
width, height = 300, 250

# --- FPS Safe Defaults ---
fps = cap.get(cv2.CAP_PROP_FPS)
fps = fps if fps > 0 else 25

# Use appropriate frame rate for streaming
if args.stream:
    fps = min(fps * 1.5, 25)  # Increase fps for streaming, max 25 fps for better performance

def rescaleframe(frame, scale=0.5):
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height)
    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)

def checkParkingSpace(imgPro, img_r):
    global prev_parking_status
    parking_status = []
    spaceCounter = 0

    for pos in posList:
        x, y = pos

        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)

        if count < 10000:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
            occupied = False
        else:
            color = (0, 0, 255)
            thickness = 2
            occupied = True

        cv2.rectangle(img_r, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img_r, str(count), (x, y + height - 3), scale=1,
                           thickness=2, offset=0, colorR=color)
        parking_status.append(occupied)

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

    checkParkingSpace(imgDilate, img_r)

    if args.stream:
        # Encode frame as JPEG
        # Encode with lower quality for faster processing and smaller size
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, 70]  # Reduce quality for speed
        ret, jpeg = cv2.imencode('.jpg', img_r, encode_params)
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
        delay = max(0.01, 1.0 / fps - elapsed)  # Minimum 10ms delay for smoother streaming
    else:
        # Normal frame rate for detection only
        delay = max(0.005, 1.0 / fps - elapsed)
    time.sleep(delay)