// Tropical Cloud Detection - Enhanced Loading Animations

class LoadingManager {
    constructor() {
        this.currentProgress = 0;
        this.targetProgress = 0;
        this.animationId = null;
        this.progressSteps = [];
        this.currentStep = 0;
    }

    // Smooth progress animation
    animateProgress(targetPercent, duration = 1000) {
        const startProgress = this.currentProgress;
        const progressDiff = targetPercent - startProgress;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutCubic = 1 - Math.pow(1 - progress, 3);
            this.currentProgress = startProgress + (progressDiff * easeOutCubic);
            
            this.updateProgressBar(this.currentProgress);
            
            if (progress < 1) {
                this.animationId = requestAnimationFrame(animate);
            }
        };

        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        this.animationId = requestAnimationFrame(animate);
    }

    // Update progress bar with smooth transitions
    updateProgressBar(percent) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        if (progressFill) {
            progressFill.style.width = percent + '%';
        }
        
        if (progressText) {
            progressText.textContent = percent.toFixed(1) + '%';
            progressText.classList.add('updating');
            setTimeout(() => progressText.classList.remove('updating'), 300);
        }
    }

    // Show processing steps with animations
    showProcessingStep(stepName, isActive = false, isCompleted = false) {
        const stepElement = document.querySelector(`[data-step="${stepName}"]`);
        if (stepElement) {
            stepElement.classList.add('processing-step');
            
            if (isActive) {
                stepElement.classList.add('active');
                stepElement.classList.remove('completed');
            } else if (isCompleted) {
                stepElement.classList.add('completed');
                stepElement.classList.remove('active');
            }
        }
    }

    // Enhanced upload progress with detailed steps
    startUploadProgress() {
        this.progressSteps = [
            { name: 'preparing', percent: 5 },
            { name: 'uploading', percent: 50 },
            { name: 'validating', percent: 75 },
            { name: 'processing', percent: 90 },
            { name: 'completing', percent: 100 }
        ];
        
        this.currentStep = 0;
        this.showProgressContainer();
        this.animateToStep(0);
    }

    animateToStep(stepIndex) {
        if (stepIndex < this.progressSteps.length) {
            const step = this.progressSteps[stepIndex];
            this.animateProgress(step.percent, 800);
            this.updateStepMessage(step.name);
            
            setTimeout(() => {
                this.currentStep = stepIndex + 1;
                if (this.currentStep < this.progressSteps.length) {
                    this.animateToStep(this.currentStep);
                }
            }, 1000);
        }
    }

    updateStepMessage(stepName) {
        const stepMessages = {
            'preparing': '🔄 Preparing file for upload...',
            'uploading': '📤 Uploading to Google Cloud Storage...',
            'validating': '✅ Validating uploaded file...',
            'processing': '⚙️ Starting cloud detection processing...',
            'completing': '🎉 Upload complete! Processing started.'
        };

        const messageElement = document.getElementById('stepMessage');
        if (messageElement) {
            messageElement.textContent = stepMessages[stepName] || stepName;
            messageElement.classList.add('fade-in');
            setTimeout(() => messageElement.classList.remove('fade-in'), 600);
        }
    }

    showProgressContainer() {
        const container = document.getElementById('progressContainer');
        if (container) {
            container.style.display = 'block';
            container.classList.add('upload-progress');
            setTimeout(() => container.classList.add('show'), 100);
        }
    }

    // Processing status animations
    startProcessingAnimation() {
        const statusElement = document.getElementById('processingStatus');
        if (statusElement) {
            statusElement.classList.add('processing-status');
            setTimeout(() => statusElement.classList.add('show'), 100);
        }
    }

    // File selection animations
    animateFileSelection(file) {
        const fileInfo = document.getElementById('fileInfo');
        if (fileInfo) {
            fileInfo.classList.add('file-info');
            setTimeout(() => fileInfo.classList.add('show'), 100);
        }
    }

    // Success animation
    showSuccess(message) {
        const status = document.getElementById('status');
        if (status) {
            status.textContent = message;
            status.className = 'status success success-animation';
            status.style.display = 'block';
        }
    }

    // Error animation
    showError(message) {
        const status = document.getElementById('status');
        if (status) {
            status.textContent = message;
            status.className = 'status error error-shake';
            status.style.display = 'block';
        }
    }

    // Reset all animations
    reset() {
        this.currentProgress = 0;
        this.targetProgress = 0;
        this.currentStep = 0;
        
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }

        const elements = [
            'progressContainer',
            'fileInfo',
            'status',
            'progressFill',
            'progressText'
        ];

        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.classList.remove('show', 'updating', 'fade-in');
                if (id === 'progressFill') {
                    element.style.width = '0%';
                }
            }
        });
    }
}

// Enhanced upload functionality
class EnhancedUploader {
    constructor() {
        this.loadingManager = new LoadingManager();
        this.selectedFile = null;
        this.maxFileSize = 100 * 1024 * 1024; // 100MB
    }

    initialize() {
        this.setupDragAndDrop();
        this.setupFileInput();
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');
        if (!uploadArea) return;

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFile(files[0]);
            }
        });
    }

    setupFileInput() {
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (event) => {
                const file = event.target.files[0];
                if (file) {
                    this.handleFile(file);
                }
            });
        }
    }

    handleFile(file) {
        // Validate file
        if (!this.validateFile(file)) {
            return;
        }

        this.selectedFile = file;
        this.displayFileInfo(file);
        this.enableUploadButton();
        this.loadingManager.showSuccess('✅ File selected and ready for upload!');
    }

    validateFile(file) {
        // Check file size
        if (file.size > this.maxFileSize) {
            this.loadingManager.showError(`❌ File size ${(file.size / 1024 / 1024).toFixed(2)}MB exceeds the 100MB limit`);
            return false;
        }

        // Check file type
        const allowedTypes = ['.h5', '.hdf5', '.nc', '.netcdf'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        if (!allowedTypes.includes(fileExtension)) {
            this.loadingManager.showError(`❌ File type ${fileExtension} is not supported. Please use HDF5 or NetCDF files.`);
            return false;
        }

        return true;
    }

    displayFileInfo(file) {
        const fileInfo = document.getElementById('fileInfo');
        if (fileInfo) {
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('fileSize').textContent = this.formatFileSize(file.size);
            document.getElementById('fileType').textContent = file.type || 'Unknown';
            this.loadingManager.animateFileSelection(file);
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    enableUploadButton() {
        const uploadBtn = document.getElementById('uploadBtn');
        if (uploadBtn) {
            uploadBtn.disabled = false;
            uploadBtn.classList.add('btn-loading');
        }
    }

    async uploadFile() {
        if (!this.selectedFile) {
            this.loadingManager.showError('❌ Please select a file first');
            return;
        }

        const uploadBtn = document.getElementById('uploadBtn');
        if (uploadBtn) {
            uploadBtn.disabled = true;
        }

        this.loadingManager.startUploadProgress();

        try {
            // Step 1: Get signed URL
            this.loadingManager.updateStepMessage('preparing');
            const response = await fetch('/get-upload-url/', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                throw new Error('Failed to get upload URL');
            }

            const data = await response.json();
            const { upload_url, filename, bucket_name } = data;

            // Step 2: Upload to GCS with progress
            this.loadingManager.updateStepMessage('uploading');
            await this.uploadToGCS(upload_url, filename);

            // Step 3: Notify backend
            this.loadingManager.updateStepMessage('validating');
            await this.notifyBackend(filename, bucket_name);

            // Step 4: Complete
            this.loadingManager.updateStepMessage('completing');
            this.loadingManager.showSuccess('🎉 Upload complete! Processing started.');
            
            setTimeout(() => this.resetForm(), 3000);

        } catch (error) {
            this.loadingManager.showError(`❌ Error: ${error.message}`);
            if (uploadBtn) uploadBtn.disabled = false;
        }
    }

    async uploadToGCS(uploadUrl, filename) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (event) => {
                if (event.lengthComputable) {
                    const percentComplete = (event.loaded / event.total) * 100;
                    this.loadingManager.animateProgress(percentComplete, 300);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    resolve();
                } else {
                    reject(new Error(`Upload failed with status: ${xhr.status}`));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Upload failed'));
            });

            xhr.open('PUT', uploadUrl);
            xhr.setRequestHeader('Content-Type', 'application/octet-stream');
            xhr.send(this.selectedFile);
        });
    }

    async notifyBackend(filename, bucketName) {
        const formData = new FormData();
        formData.append('file_name', this.selectedFile.name);
        formData.append('file_path', filename);
        formData.append('file_size', this.selectedFile.size);
        formData.append('upload_source', 'gcs');
        formData.append('gcs_bucket', bucketName);
        formData.append('gcs_path', filename);

        const response = await fetch('/upload/', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to create database record');
        }

        return await response.json();
    }

    resetForm() {
        this.selectedFile = null;
        this.loadingManager.reset();
        
        const elements = ['fileInput', 'fileInfo', 'progressContainer', 'uploadBtn'];
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                if (id === 'fileInput') element.value = '';
                else if (id === 'uploadBtn') element.disabled = true;
                else element.style.display = 'none';
            }
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const uploader = new EnhancedUploader();
    uploader.initialize();

    // Make uploader globally available
    window.enhancedUploader = uploader;
});

// Auto-refresh for processing status
if (document.querySelector('[data-processing-status]')) {
    const processingStatus = document.querySelector('[data-processing-status]').dataset.processingStatus;
    
    if (processingStatus === 'processing' || processingStatus === 'pending') {
        setTimeout(() => {
            window.location.reload();
        }, 5000);
    }
} 