#!/bin/bash

# Validation script for Docker setup

echo "🐳 Validating Docker setup for Facial Recognition Attendance System..."
echo ""

# Check if all required files exist
files=("Dockerfile" "docker-compose.yml" ".dockerignore" "build-docker.sh" "README-Docker.md")
missing_files=()

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
        missing_files+=("$file")
    fi
done

echo ""

# Check if build script is executable
if [ -x "build-docker.sh" ]; then
    echo "✓ build-docker.sh is executable"
else
    echo "✗ build-docker.sh is not executable"
    echo "  Run: chmod +x build-docker.sh"
fi

echo ""

# Check application files
app_files=("app.py" "main.py" "pyproject.toml" "face_recognition_service.py")
for file in "${app_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
        missing_files+=("$file")
    fi
done

echo ""

# Check directories
directories=("face_encodings" "face_images" "templates" "static")
for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ $dir/ directory exists"
    else
        echo "✗ $dir/ directory missing"
    fi
done

echo ""

if [ ${#missing_files[@]} -eq 0 ]; then
    echo "🎉 All Docker files are ready!"
    echo ""
    echo "Next steps:"
    echo "1. Transfer these files to a machine with Docker installed"
    echo "2. Run: ./build-docker.sh"
    echo "3. Or use: docker-compose up -d"
    echo ""
    echo "Your application will be available at http://localhost:5000"
else
    echo "❌ Some files are missing. Please ensure all required files are present."
fi