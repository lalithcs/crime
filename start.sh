#!/bin/bash

echo "========================================"
echo "Crime Safety Platform - Quick Start"
echo "========================================"
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✓ Docker found"
echo

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker Compose found"
echo

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "Creating backend/.env file..."
    cp backend/.env.example backend/.env
    echo "✓ Created backend/.env (please update with your settings)"
fi

echo
echo "Starting services with Docker Compose..."
echo
docker-compose up --build -d

echo
echo "Waiting for services to be ready..."
sleep 10

echo
echo "Running database migrations..."
docker-compose exec backend python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"

echo
echo "Loading sample crime data..."
docker-compose exec backend python scripts/ingest_data.py

echo
echo "========================================"
echo "✅ Platform is ready!"
echo "========================================"
echo
echo "Access the application:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo
echo "To stop the platform:"
echo "  docker-compose down"
echo
echo "To view logs:"
echo "  docker-compose logs -f"
echo
