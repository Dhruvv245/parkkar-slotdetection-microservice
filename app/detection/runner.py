import subprocess
import threading
import os
from app.utils.notifier import send_slot_update

# Get the virtual environment's Python executable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PYTHON_EXECUTABLE = os.path.join(BASE_DIR, "venv", "bin", "python")

def run_detection_script(parking_id: str, script_path: str):
    def run():
        process = subprocess.Popen(
            [PYTHON_EXECUTABLE, "-u", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=BASE_DIR
        )
        for line in process.stdout:
            line = line.strip()
            try:
                free_slots = int(line)
                send_slot_update(parking_id, free_slots)
            except ValueError:
                print(f"[WARN] Non-integer output: {line}")

        err = process.stderr.read()
        if err:
            print(f"[ERROR] {err}")

    threading.Thread(target=run, daemon=True).start()


def stream_video_and_detect(parking_id: str, script_path: str):
    process = subprocess.Popen(
        [PYTHON_EXECUTABLE, "-u", script_path, "--stream"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=BASE_DIR
    )

    try:
        while True:
            line = process.stdout.readline()
            if not line:
                break

            # Start of a new frame
            if line.startswith(b'--frame'):
                frame = line
                while True:
                    chunk = process.stdout.readline()
                    if not chunk or chunk.startswith(b'--frame'):
                        break
                    frame += chunk
                yield frame

    except GeneratorExit:
        # Handle client disconnect (browser closes tab)
        process.kill()
        print(f"[stream_video_and_detect] Client disconnected, killed process for {parking_id}")

    except Exception as e:
        process.kill()
        print(f"[stream_video_and_detect] Unexpected error: {e}")

    finally:
        err = process.stderr.read()
        if err:
            print(f"[stream_video_and_detect stderr] {err.decode()}")

