/**
 * Webcam utility functions for the attendance system
 */

class WebcamUtil {
    constructor(videoElement, options = {}) {
        this.video = videoElement;
        this.stream = null;
        this.options = {
            width: options.width || 640,
            height: options.height || 480,
            facingMode: options.facingMode || 'user'
        };
    }

    async start() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: this.options.width },
                    height: { ideal: this.options.height },
                    facingMode: this.options.facingMode
                }
            });
            this.video.srcObject = this.stream;
            return true;
        } catch (error) {
            console.error('Error starting webcam:', error);
            return false;
        }
    }

    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.video.srcObject = null;
            this.stream = null;
        }
    }

    captureImage() {
        if (!this.stream) return null;
        
        const canvas = document.createElement('canvas');
        canvas.width = this.video.videoWidth;
        canvas.height = this.video.videoHeight;
        
        const context = canvas.getContext('2d');
        context.drawImage(this.video, 0, 0, canvas.width, canvas.height);
        
        return canvas.toDataURL('image/jpeg');
    }

    isRunning() {
        return this.stream !== null;
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined') {
    module.exports = WebcamUtil;
}
