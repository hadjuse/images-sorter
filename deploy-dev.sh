#!/bin/bash

# Simple Development Deployment Script
# Usage: ./deploy-dev.sh

set -e

PROJECT_NAME="image-processor"

echo "🚀 Starting $PROJECT_NAME development environment..."

# Check if Docker is running
echo "🔍 Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker daemon is not accessible. This could be because:"
    echo "   1. Docker is not running"
    echo "   2. Your user is not in the docker group"
    echo "   3. You need to use sudo"
    echo ""
    echo "💡 Try one of these solutions:"
    echo "   1. Start Docker Desktop (if using Docker Desktop)"
    echo "   2. Add your user to docker group: sudo usermod -aG docker $USER"
    echo "   3. Log out and log back in after adding to docker group"
    echo "   4. Or run with sudo: sudo ./deploy-dev.sh"
    exit 1
fi

echo "✅ Docker is accessible"

# Check if Docker Compose is available
echo "🔍 Checking Docker Compose..."
if ! docker compose version > /dev/null 2>&1 && ! docker-compose --version > /dev/null 2>&1; then
    echo "❌ Docker Compose is not installed or not accessible."
    echo "   Please install Docker Compose and try again."
    exit 1
fi

# Prefer docker compose over docker-compose if available
if docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "✅ Docker Compose is available ($COMPOSE_CMD)"

echo "🔧 Building and starting development services..."

# Stop any running containers
echo "🛑 Stopping any existing containers..."
$COMPOSE_CMD -f docker-compose.dev.yml down

# Build and start services
echo "🔨 Building and starting services..."
$COMPOSE_CMD -f docker-compose.dev.yml up --build -d

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "📋 Service status:"
$COMPOSE_CMD -f docker-compose.dev.yml ps

echo ""
echo "✅ Development environment ready!"
echo ""
echo "🔗 Access your application:"
echo "  📱 Frontend: http://localhost:3000"
echo "  🔗 Backend API: http://localhost:8000"
echo "  📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "📝 Useful commands:"
echo "  View logs: $COMPOSE_CMD -f docker-compose.dev.yml logs -f"
echo "  Stop services: $COMPOSE_CMD -f docker-compose.dev.yml down"
echo "  Restart: ./deploy-dev.sh"
echo ""
echo "🎉 Happy coding!"