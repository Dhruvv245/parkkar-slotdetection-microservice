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

# --- Parse Arguments ---
parser = argparse.ArgumentParser()
parser.add_argument('--stream', action='store_true', help='Enable MJPEG streaming to stdout')
args = parser.parse_args()

# --- Config ---
PARKING_ID = "5c88fa8cf4afda39709c2974"
base_dir = os.path.dirname(__file__)
video_path = os.path.join(base_dir, 'cbb.mp4')
cbposn_path = os.path.join(base_dir, 'cbposn')

# --- Load Resources ---
cap = cv2.VideoCapture(video_path)
with open(cbposn_path, 'rb') as f:
    posList = pickle.load(f)

prev_parking_status = [False] * len(posList)
width, height = 250, 500

# --- Core Detection Function ---
def check_parking_space(img_processed):
    global prev_parking_status
    parking_status = []
    space_counter = 0

    for pos in posList:
        x, y = pos
        img_crop = img_processed[y:y + height, x:x + width]
        count = cv2.countNonZero(img_crop)

        occupied = count >= 1500
        parking_status.append(occupied)
        if not occupied:
            space_counter += 1

    if parking_status != prev_parking_status:
        prev_parking_status = parking_status
        send_slot_update(PARKING_ID, space_counter)
        print(f"[INFO] Free slots: {space_counter}", flush=True)

# --- FPS Safe Defaults ---
fps = cap.get(cv2.CAP_PROP_FPS)
fps = fps if fps > 0 else 25

# --- Main Loop ---
while True:
    start_time = time.time()
    success, img = cap.read()
    if not success:
        break

    # Image processing
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
    img_thresh = cv2.adaptiveThreshold(
        img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 25, 16
    )
    img_median = cv2.medianBlur(img_thresh, 5)
    kernel = np.ones((3, 3), np.uint8)
    img_dilate = cv2.dilate(img_median, kernel, iterations=1)

    # Detection
    check_parking_space(img_dilate)

    # MJPEG Streaming
    if args.stream:
        ret, jpeg = cv2.imencode('.jpg', img)
        if not ret:
            continue
        sys.stdout.buffer.write(b'--frame\r\n')
        sys.stdout.buffer.write(b'Content-Type: image/jpeg\r\n\r\n')
        sys.stdout.buffer.write(jpeg.tobytes())
        sys.stdout.buffer.write(b'\r\n')
        sys.stdout.flush()

    # Timing
    elapsed = time.time() - start_time
    delay = max(0.005, 1.0 / fps - elapsed)
    time.sleep(delay)
