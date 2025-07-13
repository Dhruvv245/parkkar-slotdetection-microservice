import subprocess
import threading
import os
import sys
import logging
from app.utils.notifier import send_slot_update

# Set up logging
logger = logging.getLogger(__name__)

# Determine the correct Python executable
# In Docker container or Railway deployment, use system python, otherwise use venv python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if we're running in a container or cloud deployment
is_containerized = (
    os.path.exists('/.dockerenv') or  # Docker container
    os.environ.get('DOCKER_CONTAINER') or  # Docker env var
    os.environ.get('RAILWAY_ENVIRONMENT') or  # Railway deployment
    os.environ.get('HEROKU_DYNO_ID') or  # Heroku deployment
    not os.path.exists(os.path.join(BASE_DIR, "venv"))  # No venv directory
)

if is_containerized:
    PYTHON_EXECUTABLE = sys.executable
    logger.info(f"Using containerized Python: {PYTHON_EXECUTABLE}")
else:
    # Use virtual environment when running locally
    PYTHON_EXECUTABLE = os.path.join(BASE_DIR, "venv", "bin", "python")
    logger.info(f"Using local venv Python: {PYTHON_EXECUTABLE}")

logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info(f"Python executable: {PYTHON_EXECUTABLE}")
logger.info(f"Is containerized: {is_containerized}")

def run_detection_script(parking_id: str, script_path: str):
    def run():
        try:
            logger.info(f"Starting detection for {parking_id} using {script_path}")
            logger.info(f"Using Python executable: {PYTHON_EXECUTABLE}")
            
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
                    logger.debug(f"[WARN] Non-integer output: {line}")

            err = process.stderr.read()
            if err:
                logger.error(f"[ERROR] {err}")
                
        except FileNotFoundError as e:
            logger.error(f"Python executable not found: {PYTHON_EXECUTABLE}")
            logger.error(f"Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in detection script: {e}")

    threading.Thread(target=run, daemon=True).start()


def stream_video_and_detect(parking_id: str, script_path: str):
    """Stream video with detection using optimized MJPEG format"""
    import subprocess
    
    try:
        logger.info(f"Starting optimized stream for {parking_id} using {script_path}")
        logger.info(f"Using Python executable: {PYTHON_EXECUTABLE}")
        
        # Start process with optimized settings for streaming
        process = subprocess.Popen(
            [PYTHON_EXECUTABLE, "-u", script_path, "--stream"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=BASE_DIR,
            bufsize=0,  # Unbuffered for real-time streaming
            preexec_fn=None if os.name == 'nt' else lambda: os.nice(10)  # Lower priority to prevent blocking
        )

        try:
            while True:
                # Read data in smaller chunks for lower latency
                data = process.stdout.read(4096)
                if not data:
                    break
                
                # Yield immediately for lower latency
                yield data

        except GeneratorExit:
            # Handle client disconnect (browser closes tab)
            process.terminate()
            logger.info(f"[stream_video_and_detect] Client disconnected, terminated process for {parking_id}")

        except Exception as e:
            process.terminate()
            logger.error(f"[stream_video_and_detect] Unexpected error: {e}")

        finally:
            try:
                process.terminate()
                process.wait(timeout=3)  # Shorter timeout for faster cleanup
            except subprocess.TimeoutExpired:
                process.kill()
            except:
                pass
            
            # Read any remaining stderr output
            try:
                if process.stderr:
                    err = process.stderr.read()
                    if err:
                        logger.error(f"[stream_video_and_detect stderr] {err.decode()}")
            except:
                pass
                
    except FileNotFoundError as e:
        logger.error(f"Python executable not found for streaming: {PYTHON_EXECUTABLE}")
        logger.error(f"Error: {e}")
        yield b"--frame\r\nContent-Type: text/plain\r\n\r\nError: Python executable not found\r\n"
    except Exception as e:
        logger.error(f"Failed to start streaming process: {e}")
        yield b"--frame\r\nContent-Type: text/plain\r\n\r\nError: Failed to start streaming\r\n"

