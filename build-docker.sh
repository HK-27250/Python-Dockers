#!/bin/bash

# Build script for Facial Recognition Attendance System Docker image

echo "Building Facial Recognition Attendance System Docker image..."

# Build the Docker image
docker build -t facial-recognition-attendance:latest .

if [ $? -eq 0 ]; then
    echo "✓ Docker image built successfully!"
    echo ""
    echo "To run the container:"
    echo "  docker run -p 5000:5000 -v \$(pwd)/face_images:/app/face_images -v \$(pwd)/face_encodings:/app/face_encodings facial-recognition-attendance:latest"
    echo ""
    echo "Or use docker-compose:"
    echo "  docker-compose up -d"
    echo ""
    echo "Access the application at: http://localhost:5000"
else
    echo "✗ Docker build failed!"
    exit 1
fi