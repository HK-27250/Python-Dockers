# Facial Recognition Attendance System

## Overview

This is a Flask-based facial recognition attendance system that allows student registration, face capture, and automated attendance tracking. The system provides a web interface for managing students and taking attendance through facial recognition technology.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL with psycopg2 adapter
- **Face Recognition**: Simplified face processing using MD5 hashing (placeholder for actual face recognition)
- **Storage**: File-based storage for face images and encodings
- **Session Management**: Flask sessions with configurable secret key

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5 with dark theme
- **JavaScript**: Vanilla JavaScript for webcam functionality
- **Icons**: Font Awesome for UI icons
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

## Key Components

### Application Files
- `app.py`: Main application with Flask-SQLAlchemy integration and database models
- `main.py`: Production entry point
- Database tables: `student` (id, name, roll_no, class) and `attendance` (id, student_id, date, status)

### Face Recognition
- `face_recognition_service.py`: Simplified face processing service
- Stores face images in `face_images/` directory
- Creates MD5 hashes stored in `face_encodings/` directory
- Placeholder implementation for actual face recognition libraries

### Frontend Components
- `templates/`: HTML templates with Bootstrap styling
- `static/css/`: Custom CSS for enhanced UI
- `static/js/`: JavaScript utilities for webcam and attendance features

## Data Flow

1. **Student Registration**: 
   - User inputs student details through web form
   - System validates input and checks for duplicates
   - Student data stored in PostgreSQL database
   - Face capture initiated for biometric registration

2. **Face Capture**:
   - Webcam access through browser API
   - Image captured and sent to backend
   - Face encoding generated and stored
   - Image file saved for reference

3. **Attendance Taking**:
   - Real-time webcam feed for face recognition
   - Captured images processed for face matching
   - Attendance records created with timestamp
   - Results displayed in real-time UI

4. **Reporting**:
   - Date-based attendance queries
   - Excel export functionality
   - Student management interface

## External Dependencies

### Python Packages
- Flask: Web framework
- psycopg2: PostgreSQL adapter
- pandas: Data manipulation for reports
- werkzeug: Security utilities
- hashlib: Face encoding hashing
- base64: Image encoding/decoding

### Frontend Dependencies
- Bootstrap 5: UI framework
- Font Awesome: Icon library
- Browser APIs: MediaDevices for webcam access

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT`: Database credentials
- `SESSION_SECRET`: Flask session encryption key

## Deployment Strategy

### File Structure
```
/face_images/          # Stored face images
/face_encodings/       # Face encoding files
/templates/           # HTML templates
/static/             # CSS, JS, assets
/data/               # JSON data files (fallback)
```

### Database Setup
- Automatic table creation on startup
- PostgreSQL as primary database
- Fallback to in-memory storage for development

### Security Considerations
- Input validation for student registration
- Secure filename handling for uploads
- Session-based authentication
- Environment variable configuration

### Scalability
- Database-backed storage for production
- File-based face encoding storage
- Modular architecture for easy extension

## Docker Support

### Docker Files Created
- `Dockerfile`: Multi-stage build optimized for production
- `docker-compose.yml`: Complete container orchestration setup
- `.dockerignore`: Optimized build context exclusions
- `build-docker.sh`: Automated build script with instructions
- `README-Docker.md`: Comprehensive deployment guide
- `validate-docker-setup.sh`: Setup validation script

### Docker Features
- **Base Image**: python:3.11-slim for optimal size and security
- **Health Checks**: Built-in application monitoring
- **Volume Mounting**: Persistent data storage for face images, encodings, and database
- **Environment Variables**: Configurable SESSION_SECRET and FLASK_ENV
- **Production Ready**: Optimized for deployment with gunicorn

### Deployment Options
1. **Single Container**: `docker run` with volume mounts
2. **Docker Compose**: `docker-compose up -d` for easy management
3. **Build Script**: `./build-docker.sh` for automated building

## Changelog
- July 26, 2025: Added complete Docker containerization support
- July 15, 2025: Fixed database connection issues, switched to SQLite for reliability
- July 08, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.