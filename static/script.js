document.addEventListener('DOMContentLoaded', () => {

    // =============================================
    // Grab elements
    // =============================================
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const cameraContainer = document.getElementById('cameraContainer');
    const videoElement = document.getElementById('camera-feed');
    const canvas = document.getElementById('canvas');

    const uploadTab = document.getElementById('uploadTab');
    const cameraTab = document.getElementById('cameraTab');

    const uploadButton = document.getElementById('uploadButton'); // Not used in new design, kept for reference
    const cameraButton = document.getElementById('cameraButton'); // Not used in new design, kept for reference
    const switchCameraButton = document.getElementById('switchCameraButton');
    const captureButton = document.getElementById('captureButton');

    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const preview = document.getElementById('preview');
    const errorMessage = document.getElementById('errorMessage');
    
    const initialState = document.getElementById('initial-state');
    const resultContent = document.getElementById('result-content');

    const confidenceSelect = document.getElementById('confidenceSelect');
    const modelSelect = document.getElementById('modelSelect');

    let stream = null;
    let currentFacingMode = 'environment'; // Start with rear camera

    // =============================================
    // UI State Management
    // =============================================
    
    function showResultArea() {
        loading.style.display = 'none';
        initialState.style.display = 'none';
        errorMessage.style.display = 'none';
        resultContent.style.display = 'block';
    }

    function showLoading() {
        initialState.style.display = 'none';
        errorMessage.style.display = 'none';
        resultContent.style.display = 'none';
        loading.style.display = 'flex';
    }

    function showInitialState() {
        loading.style.display = 'none';
        errorMessage.style.display = 'none';
        resultContent.style.display = 'none';
        initialState.style.display = 'block';
    }

    function showError(message) {
        loading.style.display = 'none';
        initialState.style.display = 'none';
        resultContent.style.display = 'none';
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }


    // Tab switching logic
    uploadTab.addEventListener('click', () => {
        cameraTab.classList.remove('active');
        uploadTab.classList.add('active');
        cameraContainer.style.display = 'none';
        dropZone.style.display = 'block';
        stopCamera();
    });

    cameraTab.addEventListener('click', () => {
        uploadTab.classList.remove('active');
        cameraTab.classList.add('active');
        dropZone.style.display = 'none';
        cameraContainer.style.display = 'block';
        startCamera();
    });

    // =============================================
    // Camera Logic
    // =============================================
    async function startCamera() {
        if (stream) stopCamera(); // Stop existing stream first

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showError('Kamera tidak didukung pada browser atau koneksi Anda.');
            return;
        }

        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: currentFacingMode,
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            });
            videoElement.srcObject = stream;
            videoElement.style.transform = (currentFacingMode === 'user') ? 'scaleX(-1)' : 'scaleX(1)';
        } catch (err) {
            console.error('Camera error:', err);
            showError(`Kesalahan Kamera: ${err.message}`);
        }
    }

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
            videoElement.srcObject = null;
        }
    }

    switchCameraButton.addEventListener('click', () => {
        currentFacingMode = currentFacingMode === 'environment' ? 'user' : 'environment';
        startCamera(); // Restart camera with the new facing mode
    });
    
    // =============================================
    // File Handling & API Call
    // =============================================
    
    // Drag and drop handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-violet-500', 'bg-violet-50');
    });
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('border-violet-500', 'bg-violet-50');
    });
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-violet-500', 'bg-violet-50');
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    // File input click handler
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFile(file);
    });

    // Capture button handler
    captureButton.addEventListener('click', () => {
        if (!stream) {
            showError('Kamera tidak tersedia.');
            return;
        }
        
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        const context = canvas.getContext('2d');
        
        // Flip the image if it's from the front camera
        if (currentFacingMode === 'user') {
            context.translate(canvas.width, 0);
            context.scale(-1, 1);
        }

        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob((blob) => {
            handleFile(blob, 'capture.jpg');
        }, 'image/jpeg', 0.95);
    });


    function handleFile(file, fileName = 'uploaded_image.jpg') {
        if (!file) return;

        showLoading();

        const formData = new FormData();
        formData.append('file', file, fileName);
        formData.append('model', modelSelect.value);
        formData.append('confidence', confidenceSelect.value);

        fetch('/detect', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                showError(`Error: ${data.error}`);
                return;
            }
            
            showResultArea();
            result.textContent = `Terdeteksi ${data.count} objek`;
            // Add a cache-busting query parameter to ensure the new image is loaded
            preview.src = `/uploads/${data.image}?t=${new Date().getTime()}`;
        })
        .catch(error => {
            console.error('Fetch error:', error);
            showError(`Gagal memproses gambar: ${error.message}`);
        });
    }

    // =============================================
    // Page cleanup
    // =============================================
    window.addEventListener('beforeunload', stopCamera);
});