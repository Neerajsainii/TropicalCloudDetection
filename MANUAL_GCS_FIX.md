# 🔧 Manual Google Cloud Storage Fix

## 🚨 **Current Issue**
The `/get-upload-url/` endpoint returns `upload_method: "server_side"` because the Cloud Run service account doesn't have proper permissions to generate signed URLs for Google Cloud Storage.

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

### **Step 5: Alternative - Use gcloud CLI**
If you have gcloud CLI installed, run these commands:

```bash
# Set project
gcloud config set project tropical-cloud-detection

# Grant IAM roles
gcloud projects add-iam-policy-binding tropical-cloud-detection \
  --member=serviceAccount:1065844967286-compute@developer.gserviceaccount.com \
  --role=roles/storage.objectViewer

gcloud projects add-iam-policy-binding tropical-cloud-detection \
  --member=serviceAccount:1065844967286-compute@developer.gserviceaccount.com \
  --role=roles/storage.objectCreator

gcloud projects add-iam-policy-binding tropical-cloud-detection \
  --member=serviceAccount:1065844967286-compute@developer.gserviceaccount.com \
  --role=roles/storage.legacyBucketReader

# Create bucket if it doesn't exist
gsutil mb -p tropical-cloud-detection -c STANDARD -l us-central1 gs://tropical-cloud-detection-uploads

# Grant bucket-specific permissions
gcloud storage buckets add-iam-policy-binding gs://tropical-cloud-detection-uploads \
  --member=serviceAccount:1065844967286-compute@developer.gserviceaccount.com \
  --role=roles/storage.objectViewer

gcloud storage buckets add-iam-policy-binding gs://tropical-cloud-detection-uploads \
  --member=serviceAccount:1065844967286-compute@developer.gserviceaccount.com \
  --role=roles/storage.objectCreator
```

### **Step 6: Test the Fix**
After applying the permissions, test the endpoint:

```bash
curl -s "https://tropical-cloud-detection-1065844967286.us-central1.run.app/get-upload-url/" | python -m json.tool
```

You should see a response with `upload_url` field instead of `upload_method: "server_side"`.

### **Step 7: Deploy Updated Code**
After fixing permissions, deploy the updated code with better error handling:

```bash
# If you have gcloud installed:
gcloud run deploy tropical-cloud-detection --source . --region=us-central1 --project=tropical-cloud-detection --allow-unauthenticated --memory=3Gi --cpu=2 --timeout=300 --max-instances=5
```

## 🎯 **Expected Result**
After the fix, the `/get-upload-url/` endpoint should return:
```json
{
  "upload_url": "https://storage.googleapis.com/...",
  "filename": "satellite_data_xxx.h5",
  "bucket_name": "tropical-cloud-detection-uploads",
  "upload_method": "signed_url"
}
```

Instead of:
```json
{
  "filename": "satellite_data_xxx.h5",
  "bucket_name": "tropical-cloud-detection-uploads", 
  "upload_method": "server_side",
  "message": "Signed URL generation failed. Please use the regular upload form for files under 32MB."
}
```

## 🔍 **Troubleshooting**
If the fix doesn't work immediately:
1. Wait 5-10 minutes for permissions to propagate
2. Check Cloud Run logs for specific error messages
3. Verify the service account has the correct permissions
4. Ensure the bucket exists and is accessible 