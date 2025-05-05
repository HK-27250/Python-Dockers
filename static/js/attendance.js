/**
 * Attendance system utilities for face recognition
 */

// Helper function to create attendance record entries
function createAttendanceEntry(data, timeString) {
    const listItem = document.createElement('div');
    listItem.className = 'list-group-item';
    
    if (data.duplicate) {
        // Already marked attendance
        listItem.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <span class="status-icon text-warning">
                        <i class="fas fa-exclamation-circle"></i>
                    </span>
                    <strong>${data.name}</strong> (${data.roll_no})
                </div>
                <span class="badge bg-warning text-dark">${timeString}</span>
            </div>
            <small class="text-muted">Already marked present</small>
        `;
    } else {
        // New attendance marking
        listItem.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <span class="status-icon text-success">
                        <i class="fas fa-check-circle"></i>
                    </span>
                    <strong>${data.name}</strong> (${data.roll_no})
                </div>
                <span class="badge bg-success">${timeString}</span>
            </div>
            <small class="text-muted">Marked present</small>
        `;
    }
    
    return listItem;
}

// Helper to format current date/time
function getCurrentDateTime() {
    const now = new Date();
    return {
        date: now.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        }),
        time: now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        })
    };
}

// Send captured image to server for recognition
async function recognizeFace(imageData) {
    try {
        const formData = new FormData();
        formData.append('image_data', imageData);
        
        const response = await fetch('/recognize', {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    } catch (error) {
        console.error('Recognition error:', error);
        return {
            success: false,
            message: `Error: ${error.message}`
        };
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined') {
    module.exports = {
        createAttendanceEntry,
        getCurrentDateTime,
        recognizeFace
    };
}
