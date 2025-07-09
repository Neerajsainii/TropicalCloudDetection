// Large File Upload Handler for Google Cloud Storage
// This handles files larger than 32MB by uploading directly to GCS

class LargeFileUploader {
    constructor() {
        this.maxFileSize = 100 * 1024 * 1024; // 100MB
        this.chunkSize = 5 * 1024 * 1024; // 5MB chunks
    }

    async uploadLargeFile(file, progressCallback = null) {
        try {
            // Check file size
            if (file.size > this.maxFileSize) {
                throw new Error(`File size ${(file.size / 1024 / 1024).toFixed(2)}MB exceeds maximum allowed size of ${this.maxFileSize / 1024 / 1024}MB`);
            }

            // Get signed URL from server
            const response = await fetch('/get-upload-url/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error('Failed to get upload URL');
            }

            const data = await response.json();
            const { upload_url, filename, bucket_name } = data;

            // Upload file directly to Google Cloud Storage
            const uploadResponse = await fetch(upload_url, {
                method: 'PUT',
                body: file,
                headers: {
                    'Content-Type': 'application/octet-stream',
                }
            });

            if (!uploadResponse.ok) {
                throw new Error('Failed to upload file to Google Cloud Storage');
            }

            // Create database record
            const formData = new FormData();
            formData.append('file_name', file.name);
            formData.append('file_path', filename);
            formData.append('file_size', file.size);
            formData.append('upload_source', 'gcs');
            formData.append('gcs_bucket', bucket_name);
            formData.append('gcs_path', filename);

            const dbResponse = await fetch('/upload/', {
                method: 'POST',
                body: formData
            });

            if (!dbResponse.ok) {
                throw new Error('Failed to create database record');
            }

            const result = await dbResponse.json();
            return result;

        } catch (error) {
            console.error('Upload failed:', error);
            throw error;
        }
    }

    async uploadWithProgress(file, progressCallback = null) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            // Get signed URL first
            fetch('/get-upload-url/')
                .then(response => response.json())
                .then(data => {
                    const { upload_url, filename, bucket_name } = data;
                    
                    xhr.upload.addEventListener('progress', (event) => {
                        if (event.lengthComputable && progressCallback) {
                            const percentComplete = (event.loaded / event.total) * 100;
                            progressCallback(percentComplete);
                        }
                    });

                    xhr.addEventListener('load', async () => {
                        if (xhr.status === 200) {
                            try {
                                // Create database record
                                const formData = new FormData();
                                formData.append('file_name', file.name);
                                formData.append('file_path', filename);
                                formData.append('file_size', file.size);
                                formData.append('upload_source', 'gcs');
                                formData.append('gcs_bucket', bucket_name);
                                formData.append('gcs_path', filename);

                                const dbResponse = await fetch('/upload/', {
                                    method: 'POST',
                                    body: formData
                                });

                                if (dbResponse.ok) {
                                    const result = await dbResponse.json();
                                    resolve(result);
                                } else {
                                    reject(new Error('Failed to create database record'));
                                }
                            } catch (error) {
                                reject(error);
                            }
                        } else {
                            reject(new Error(`Upload failed with status: ${xhr.status}`));
                        }
                    });

                    xhr.addEventListener('error', () => {
                        reject(new Error('Upload failed'));
                    });

                    xhr.open('PUT', upload_url);
                    xhr.setRequestHeader('Content-Type', 'application/octet-stream');
                    xhr.send(file);
                })
                .catch(reject);
        });
    }
}

// Usage example:
/*
const uploader = new LargeFileUploader();

document.getElementById('fileInput').addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
        try {
            const result = await uploader.uploadWithProgress(file, (progress) => {
                console.log(`Upload progress: ${progress.toFixed(2)}%`);
                // Update progress bar
                document.getElementById('progressBar').style.width = progress + '%';
            });
            console.log('Upload successful:', result);
        } catch (error) {
            console.error('Upload failed:', error);
        }
    }
});
*/ 