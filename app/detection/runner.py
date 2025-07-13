import subprocess
import threading
import os
import sys
from app.utils.notifier import send_slot_update

# Determine the correct Python executable
# In Docker container, use system python, otherwise use venv python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if we're running in a container (no venv needed)
if os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER'):
    PYTHON_EXECUTABLE = sys.executable
else:
    # Use virtual environment when running locally
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
    """Stream video with detection using proper MJPEG format"""
    import subprocess
    
    # Start process with binary stdout to handle MJPEG data
    process = subprocess.Popen(
        [PYTHON_EXECUTABLE, "-u", script_path, "--stream"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=BASE_DIR,
        bufsize=0  # Unbuffered for real-time streaming
    )

    try:
        while True:
            # Read data from the process in larger chunks for better performance
            data = process.stdout.read(8192)
            if not data:
                break
            
            # Yield the raw binary data as received from the script
            yield data

    except GeneratorExit:
        # Handle client disconnect (browser closes tab)
        process.terminate()
        print(f"[stream_video_and_detect] Client disconnected, terminated process for {parking_id}")

    except Exception as e:
        process.terminate()
        print(f"[stream_video_and_detect] Unexpected error: {e}")

    finally:
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        except:
            pass
        
        # Read any remaining stderr output
        try:
            if process.stderr:
                err = process.stderr.read()
                if err:
                    print(f"[stream_video_and_detect stderr] {err.decode()}")
        except:
            pass

