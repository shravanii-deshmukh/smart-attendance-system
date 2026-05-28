// Elements
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('capture-btn');
const statusMessage = document.getElementById('status-message');

// API endpoint URL (passed from HTML via data attribute)
let apiEndpoint = '';
// Additional form data (like name, prn, phone)
let getFormData = null;
// Redirect URL on success
let redirectUrl = '';

// Initialize Webcam
async function initWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        console.error("Error accessing webcam: ", err);
        showStatus("Error accessing webcam. Please make sure it is connected and allowed.", "error");
    }
}

// Setup configuration from HTML
function setupWebcam(endpoint, redirect, formCallback = null) {
    apiEndpoint = endpoint;
    redirectUrl = redirect;
    getFormData = formCallback;
    initWebcam();
}

// Capture and Send
if (captureBtn) {
    captureBtn.addEventListener('click', async () => {
        // Draw video frame to canvas
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Get Base64 image data
        const imageData = canvas.toDataURL('image/jpeg');
        
        // Prepare payload
        let payload = { image: imageData };
        
        // If this is enrollment, we need extra form data
        if (getFormData) {
            const extraData = getFormData();
            if (!extraData) return; // Validation failed
            payload = { ...payload, ...extraData };
        }
        
        // Update UI
        captureBtn.disabled = true;
        captureBtn.innerText = "Processing...";
        showStatus("Analyzing Face... Please wait.", "info");
        
        try {
            const response = await fetch(apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                showStatus(result.message, "success");
                setTimeout(() => {
                    window.location.href = redirectUrl;
                }, 2000);
            } else {
                showStatus(result.error || "An error occurred.", "error");
                captureBtn.disabled = false;
                captureBtn.innerText = "Try Again";
            }
        } catch (error) {
            console.error("API Error: ", error);
            showStatus("Failed to communicate with server.", "error");
            captureBtn.disabled = false;
            captureBtn.innerText = "Try Again";
        }
    });
}

function showStatus(message, type) {
    if (!statusMessage) return;
    statusMessage.innerText = message;
    statusMessage.style.color = type === 'error' ? 'var(--danger-color)' : 
                                type === 'success' ? 'var(--success-color)' : 'var(--text-muted)';
}
