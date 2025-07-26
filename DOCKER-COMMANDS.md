# Docker Commands Reference

## Building the Image

### Windows PowerShell
```powershell
docker build -t attendance-app .
```

### Linux/Mac Terminal
```bash
docker build -t attendance-app .
```

### Using the Build Scripts
```bash
# Linux/Mac
./build-docker.sh

# Windows PowerShell
./build-docker.ps1
```

## Running the Container

### Basic Run
```bash
docker run -p 5000:5000 attendance-app
```

### With Data Persistence (Recommended)
```bash
# Linux/Mac
docker run -p 5000:5000 \
  -v $(pwd)/face_images:/app/face_images \
  -v $(pwd)/face_encodings:/app/face_encodings \
  -v $(pwd)/attendance.db:/app/attendance.db \
  attendance-app

# Windows PowerShell
docker run -p 5000:5000 \
  -v ${PWD}/face_images:/app/face_images \
  -v ${PWD}/face_encodings:/app/face_encodings \
  -v ${PWD}/attendance.db:/app/attendance.db \
  attendance-app
```

### Background Mode
```bash
docker run -d -p 5000:5000 \
  -v $(pwd)/face_images:/app/face_images \
  -v $(pwd)/face_encodings:/app/face_encodings \
  attendance-app
```

## Docker Compose (Easiest)
```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Useful Docker Commands

### View Running Containers
```bash
docker ps
```

### View Container Logs
```bash
docker logs <container-id>
```

### Stop Container
```bash
docker stop <container-id>
```

### Remove Container
```bash
docker rm <container-id>
```

### Remove Image
```bash
docker rmi attendance-app
```

## Access Application
Once running, open your browser to: **http://localhost:5000**