from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
import logging
from app.detection.runner import run_detection_script, stream_video_and_detect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ParkKar Slot Detection API",
    description="Real-time parking slot detection and streaming service",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("ParkKar Detection Service starting up...")
    logger.info(f"Available parking scripts: {len(PARKING_SCRIPTS)}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("ParkKar Detection Service shutting down...")

# Map of parking lot IDs to script names
PARKING_SCRIPTS = {
    '5c88fa8cf4afda39709c2974': 'cb_parking_detector.py',
    '5c88fa8cf4afda39709c2970': 'chemistry_parking_detector.py',
    '661661e96104b67c07d092ec': 'workshop_parking_detector.py',
    '68700289a320c9d36bd397a4': 'kbh_parking_detector.py',
}

class SlotUpdatePayload(BaseModel):
    parkingId: str
    freeSlots: int

@app.get("/")
def root():
    return {"message": "ParkKar Slot Detection API", "version": "1.0.0", "status": "running"}

@app.get("/health")
def health_check():
    """Health check endpoint for Railway deployment"""
    try:
        return {
            "status": "healthy", 
            "service": "parkkar-detection",
            "version": "1.0.0",
            "parking_lots_available": len(PARKING_SCRIPTS)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/parking-lots")
def get_parking_lots():
    return {
        "parking_lots": list(PARKING_SCRIPTS.keys()),
        "total": len(PARKING_SCRIPTS)
    }

@app.get("/detect/{parking_id}")
def run_detection(parking_id: str):
    if parking_id not in PARKING_SCRIPTS:
        raise HTTPException(status_code=404, detail="Invalid parking lot ID")

    script_name = PARKING_SCRIPTS[parking_id]
    script_path = os.path.join(os.path.dirname(__file__), "detection", "scripts", script_name)
    run_detection_script(parking_id, script_path)
    return {"status": "Detection started"}

@app.get("/stream/{parking_id}")
def stream_and_detect(parking_id: str):
    """Stream video with real-time parking detection - optimized for low latency"""
    if parking_id not in PARKING_SCRIPTS:
        raise HTTPException(status_code=404, detail="Invalid parking lot ID")

    script_name = PARKING_SCRIPTS[parking_id]
    script_path = os.path.join(os.path.dirname(__file__), "detection", "scripts", script_name)
    
    # Check if script file exists
    if not os.path.exists(script_path):
        logger.error(f"Detection script not found: {script_path}")
        raise HTTPException(status_code=404, detail="Detection script not found")

    try:
        return StreamingResponse(
            stream_video_and_detect(parking_id, script_path),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering for lower latency
            }
        )
    except Exception as e:
        logger.error(f"Error starting stream for {parking_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to start video stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
