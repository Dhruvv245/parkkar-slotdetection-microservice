# ParkKar Detection Microservice - Deployment Guide

## 🚀 Railway Deployment

This microservice is configured for deployment on Railway using GitHub integration.

### Deployment Configuration

- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`
- **Health Check**: `/health` endpoint
- **Build**: Nixpacks with Python 3.11 and OpenCV dependencies

### Environment Variables

The service will automatically use:

- `NODE_SERVER_URL`: Points to your main ParkKar production service
- `PORT`: Automatically set by Railway

### API Endpoints

Once deployed, the service provides:

- `GET /` - Service info
- `GET /health` - Health check
- `GET /parking-lots` - List all parking lots
- `GET /stream/{parking_id}` - Live video stream
- `GET /detect/{parking_id}` - Run detection

### Parking Lot IDs

- CB Parking: `5c88fa8cf4afda39709c2974`
- Chemistry Parking: `5c88fa8cf4afda39709c2970`
- Workshop Parking: `661661e96104b67c07d092ec`
- KBH Parking: `68700289a320c9d36bd397a4`

### Integration

The deployed service will automatically send slot updates to:
`https://parkkar-production.up.railway.app/api/v1/parkings/slot-update`
