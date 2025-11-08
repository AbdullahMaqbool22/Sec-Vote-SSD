#!/bin/bash

# Sec-Vote Platform Setup Script

echo "==================================="
echo "Sec-Vote Platform Setup"
echo "==================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker found"
echo "✓ Docker Compose found"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠️  Please update .env file with your configuration!"
else
    echo "✓ .env file already exists"
fi

# Build and start services
echo ""
echo "Building Docker containers..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."
curl -s http://localhost:8080/health | python -m json.tool

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Services are running:"
echo "  API Gateway:      http://localhost:8080"
echo "  Auth Service:     http://localhost:5001"
echo "  Poll Service:     http://localhost:5002"
echo "  Vote Service:     http://localhost:5003"
echo "  Results Service:  http://localhost:5004"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo ""
