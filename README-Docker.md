# Docker Deployment Guide

This guide explains how to build and run the Facial Recognition Attendance System using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)

## Quick Start

### Option 1: Using the Build Script

```bash
# Make the script executable (if not already)
chmod +x build-docker.sh

# Build the Docker image
./build-docker.sh
```

### Option 2: Manual Docker Build

```bash
# Build the Docker image
docker build -t facial-recognition-attendance:latest .

# Run the container
docker run -p 5000:5000 \
  -v $(pwd)/face_images:/app/face_images \
  -v $(pwd)/face_encodings:/app/face_encodings \
  -v $(pwd)/attendance.db:/app/attendance.db \
  facial-recognition-attendance:latest
```

### Option 3: Using Docker Compose

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

## Environment Variables

You can customize the application using environment variables:

- `SESSION_SECRET`: Flask session secret key (recommended to change in production)
- `FLASK_ENV`: Set to `production` for production deployment

Example with custom environment variables:

```bash
docker run -p 5000:5000 \
  -e SESSION_SECRET="your-custom-secret-key" \
  -e FLASK_ENV="production" \
  -v $(pwd)/face_images:/app/face_images \
  -v $(pwd)/face_encodings:/app/face_encodings \
  facial-recognition-attendance:latest
```

## Data Persistence

The application uses volumes to persist data:

- `face_images/`: Stores captured face images
- `face_encodings/`: Stores face encoding data
- `attendance.db`: SQLite database file

These directories are automatically mounted to preserve data between container restarts.

## Accessing the Application

Once the container is running, access the application at:
- **URL**: http://localhost:5000

## Health Monitoring

The Docker container includes a health check that monitors the application status. You can check the health status using:

```bash
docker ps
```

Look for the health status in the STATUS column.

## Troubleshooting

### Container Won't Start
- Check if port 5000 is already in use: `netstat -an | grep 5000`
- View container logs: `docker logs <container-name>`

### Permission Issues
- Ensure the face_images and face_encodings directories have proper permissions
- On Linux/Mac: `chmod 755 face_images face_encodings`

### Database Issues
- If the SQLite database gets corrupted, stop the container and delete `attendance.db`
- The application will create a new database on next startup

## Production Deployment

For production deployment:

1. Change the SESSION_SECRET environment variable
2. Consider using a reverse proxy (nginx) for SSL termination
3. Set up proper logging and monitoring
4. Consider using external storage for face images and encodings
5. Implement backup strategies for the database

## Image Information

- **Base Image**: python:3.11-slim
- **Exposed Port**: 5000
- **Working Directory**: /app
- **Health Check**: Included
- **Size**: Optimized for production use