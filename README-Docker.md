# 🐳 ParkKar Detection Service - Docker Deployment

## ✅ **Containerization Complete!**

Your parking slot detection service has been successfully containerized and is ready for deployment.

### 🚀 **Quick Start**

```bash
# Build and start the service
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### 📊 **Service Endpoints**

- **Main API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Parking Lots List**: http://localhost:8000/parking-lots
- **Video Streaming**: http://localhost:8000/stream/{parking_id}
- **Detection Trigger**: http://localhost:8000/detect/{parking_id}

### 🏗️ **Available Parking IDs**

- `5c88fa8cf4afda39709c2974` - CB Parking
- `5c88fa8cf4afda39709c2970` - Chemistry Parking
- `661661e96104b67c07d092ec` - Workshop Parking
- `68700289a320c9d36bd397a4` - KBH Parking

### 🔧 **Build Scripts**

```bash
# Use the build script
./build.sh

# Use the deployment script
./deploy.sh
```

### 📦 **Docker Images**

- **Development**: `Dockerfile`
- **Production**: `Dockerfile.prod`
- **Minimal**: `Dockerfile.minimal`

### ⚙️ **Environment Configuration**

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

### 🌐 **Production Deployment**

For production deployment on cloud platforms:

```bash
# Build production image
docker build -f Dockerfile.prod -t parkkar-detection:prod .

# Run with production settings
docker run -d \
  --name parkkar-detection \
  -p 8000:8000 \
  --restart unless-stopped \
  -e NODE_SERVER_URL=https://your-backend.com/api/v1/parkings/slot-update \
  parkkar-detection:prod
```

### 🏥 **Health Monitoring**

The service includes built-in health checks:

- Container health checks every 30s
- Python-based health endpoint
- Automatic restart on failure

### 📝 **Docker Compose Services**

```yaml
services:
  parkkar-detection:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NODE_SERVER_URL=http://host.docker.internal:3000/api/v1/parkings/slot-update
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test:
        [
          "CMD",
          "python",
          "-c",
          "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)",
        ]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 🐛 **Troubleshooting**

```bash
# Check container logs
docker-compose logs parkkar-detection

# Access container shell
docker-compose exec parkkar-detection bash

# Rebuild completely
docker-compose down --volumes --remove-orphans
docker-compose up -d --build --force-recreate
```

### 🚀 **Deployment Platforms**

This container is ready to deploy on:

- ✅ Docker Swarm
- ✅ Kubernetes
- ✅ AWS ECS/Fargate
- ✅ Google Cloud Run
- ✅ Azure Container Instances
- ✅ Digital Ocean App Platform
- ✅ Railway
- ✅ Render
- ✅ Fly.io

---

**🎉 Your parking detection service is now fully containerized and production-ready!**
