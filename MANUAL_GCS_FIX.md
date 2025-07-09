# 🔧 Manual Google Cloud Storage Fix

## 🚨 **Current Issue**
The `/get-upload-url/` endpoint returns 500 error because the Cloud Run service account doesn't have proper permissions to access Google Cloud Storage.

## 🛠️ **Manual Fix Steps**

### **Step 1: Access Google Cloud Console**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select project: `tropical-cloud-detection`

### **Step 2: Grant IAM Permissions**
1. Navigate to **IAM & Admin** → **IAM**
2. Find the service account: `1065844967286-compute@developer.gserviceaccount.com`
3. Click the **pencil icon** to edit
4. Add these roles:
   - `Storage Object Viewer` (storage.objectViewer)
   - `Storage Object Creator` (storage.objectCreator)
   - `Storage Legacy Bucket Reader` (storage.legacyBucketReader)

### **Step 3: Create/Verify Bucket**
1. Go to **Cloud Storage** → **Buckets**
2. Check if bucket `tropical-cloud-detection-uploads` exists
3. If not, create it:
   - Click **CREATE BUCKET**
   - Name: `tropical-cloud-detection-uploads`
   - Location: `us-central1`
   - Class: `Standard`

### **Step 4: Grant Bucket-Specific Permissions**
1. Go to **Cloud Storage** → **Buckets**
2. Click on `tropical-cloud-detection-uploads`
3. Go to **PERMISSIONS** tab
4. Click **GRANT ACCESS**
5. Add service account: `1065844967286-compute@developer.gserviceaccount.com`
6. Grant these roles:
   - `Storage Object Viewer`
   - `Storage Object Creator`
   - `Storage Legacy Bucket Reader`

### **Step 5: Deploy Updated Code**
After fixing permissions, deploy the updated code with better error handling:

```bash
# If you have gcloud installed:
gcloud run deploy tropical-cloud-detection --source . --region=us-central1 --project=tropical-cloud-detection --allow-unauthenticated --memory=3Gi --cpu=2 --timeout=300 --max-instances=5
```

### **Step 6: Test the Fix**
1. Go to: https://tropical-cloud-detection-1065844967286.us-central1.run.app/upload-large/
2. Try uploading a file
3. Check if `/get-upload-url/` now works

## 🔍 **Alternative: Use gcloud Commands**

If you install Google Cloud SDK, run these commands:

```bash
# Set project
gcloud config set project tropical-cloud-detection

# Grant permissions
gsutil iam ch serviceAccount:1065844967286-compute@developer.gserviceaccount.com:objectViewer gs://tropical-cloud-detection-uploads
gsutil iam ch serviceAccount:1065844967286-compute@developer.gserviceaccount.com:objectCreator gs://tropical-cloud-detection-uploads
gsutil iam ch serviceAccount:1065844967286-compute@developer.gserviceaccount.com:legacyBucketReader gs://tropical-cloud-detection-uploads

# Create bucket if it doesn't exist
gsutil mb -p tropical-cloud-detection gs://tropical-cloud-detection-uploads
```

## 📊 **Expected Result**
After fixing permissions, the `/get-upload-url/` endpoint should return:
```json
{
  "upload_url": "https://storage.googleapis.com/...",
  "filename": "satellite_data_uuid.h5",
  "bucket_name": "tropical-cloud-detection-uploads"
}
```

## 🚨 **If Still Getting 500 Errors**
1. Check Cloud Run logs in Google Cloud Console
2. Look for specific error messages
3. Verify the service account has all required permissions
4. Ensure the bucket exists and is accessible 