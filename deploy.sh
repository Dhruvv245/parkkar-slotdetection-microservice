#!/bin/bash

# Deployment script for ParkKar Detection Service
set -e

echo "🚀 Deploying ParkKar Detection Service..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Pull latest changes (if using Git)
if [ -d ".git" ]; then
    echo "📥 Pulling latest changes..."
    git pull origin main
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo "🔍 Checking service health..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Service is healthy!"
        break
    else
        echo "⏳ Waiting for service... ($i/30)"
        sleep 2
    fi
    
    if [ $i -eq 30 ]; then
        echo "❌ Service failed to start properly"
        docker-compose logs
        exit 1
    fi
done

echo "🎉 Deployment completed successfully!"
echo "📊 Service is running at: http://localhost:8000"
echo "📱 Health check: http://localhost:8000/health"
echo "📋 API docs: http://localhost:8000/docs"

# Show running containers
echo "📦 Running containers:"
docker-compose ps
