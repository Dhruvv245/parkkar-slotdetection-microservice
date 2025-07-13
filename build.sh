#!/bin/bash

# Build script for ParkKar Detection Service
set -e

echo "🔨 Building ParkKar Detection Service..."

# Build the Docker image
docker build -t parkkar-detection:latest .

echo "✅ Build completed successfully!"

# Optional: Tag for production
read -p "Tag for production? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker tag parkkar-detection:latest parkkar-detection:prod
    echo "✅ Tagged as production image"
fi

echo "📋 Available images:"
docker images | grep parkkar-detection

echo "🚀 To run the service, use:"
echo "   docker-compose up -d"
echo "   or"
echo "   docker run -p 8000:8000 parkkar-detection:latest"
