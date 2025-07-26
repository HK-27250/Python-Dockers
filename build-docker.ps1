# PowerShell script to build Facial Recognition Attendance System Docker image

Write-Host "Building Facial Recognition Attendance System Docker image..." -ForegroundColor Green

# Build the Docker image
docker build -t attendance-app .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker image built successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To run the container:" -ForegroundColor Yellow
    Write-Host "  docker run -p 5000:5000 -v ${PWD}/face_images:/app/face_images -v ${PWD}/face_encodings:/app/face_encodings attendance-app" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or use docker-compose:" -ForegroundColor Yellow
    Write-Host "  docker-compose up -d" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Access the application at: http://localhost:5000" -ForegroundColor Green
} else {
    Write-Host "✗ Docker build failed!" -ForegroundColor Red
    exit 1
}