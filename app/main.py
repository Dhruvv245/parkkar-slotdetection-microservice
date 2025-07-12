from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
from app.detection.runner import run_detection_script, stream_video_and_detect

app = FastAPI()

# Map of parking lot IDs to script names
PARKING_SCRIPTS = {
    '5c88fa8cf4afda39709c2974': 'cb.py',
    '5c88fa8cf4afda39709c2970': 'chemcounter.py',
    '661661e96104b67c07d092ec': 'workshopcounter.py',
    '68700289a320c9d36bd397a4': 'kbhcounter.py',
}

class SlotUpdatePayload(BaseModel):
    parkingId: str
    freeSlots: int

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
    if parking_id not in PARKING_SCRIPTS:
        raise HTTPException(status_code=404, detail="Invalid parking lot ID")

    script_name = PARKING_SCRIPTS[parking_id]
    script_path = os.path.join(os.path.dirname(__file__), "detection", "scripts", script_name)

    return StreamingResponse(
        stream_video_and_detect(parking_id, script_path),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
