#!/usr/bin/env python3
"""
Script to check and fix Google Cloud Storage IAM permissions for Cloud Run service
"""

import subprocess
import sys
import json

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔧 Checking and fixing Google Cloud Storage permissions...")
    
    # Project and service details
    PROJECT_ID = "tropical-cloud-detection"
    SERVICE_NAME = "tropical-cloud-detection"
    REGION = "us-central1"
    BUCKET_NAME = "tropical-cloud-detection-uploads"
    
    print(f"📋 Project: {PROJECT_ID}")
    print(f"📋 Service: {SERVICE_NAME}")
    print(f"📋 Region: {REGION}")
    print(f"📋 Bucket: {BUCKET_NAME}")
    
    # Step 1: Get the Cloud Run service account
    print("\n1️⃣ Getting Cloud Run service account...")
    success, stdout, stderr = run_command(
        f'gcloud run services describe {SERVICE_NAME} --region={REGION} --project={PROJECT_ID} --format="value(spec.template.spec.serviceAccountName)"'
    )
    
    if not success:
        print(f"❌ Failed to get service account: {stderr}")
        return
    
    service_account = stdout.strip()
    if not service_account:
        # Use default compute service account
        service_account = f"{PROJECT_ID}-compute@developer.gserviceaccount.com"
    
    print(f"✅ Service account: {service_account}")
    
    # Step 2: Check if bucket exists
    print("\n2️⃣ Checking if bucket exists...")
    success, stdout, stderr = run_command(
        f'gsutil ls -b gs://{BUCKET_NAME}'
    )
    
    if not success:
        print(f"❌ Bucket {BUCKET_NAME} does not exist. Creating it...")
        success, stdout, stderr = run_command(
            f'gsutil mb -p {PROJECT_ID} gs://{BUCKET_NAME}'
        )
        if not success:
            print(f"❌ Failed to create bucket: {stderr}")
            return
        print(f"✅ Bucket {BUCKET_NAME} created successfully")
    else:
        print(f"✅ Bucket {BUCKET_NAME} exists")
    
    # Step 3: Grant IAM permissions to the service account
    print("\n3️⃣ Granting IAM permissions...")
    
    # Grant storage.objectViewer role
    print("   📤 Granting storage.objectViewer role...")
    success, stdout, stderr = run_command(
        f'gsutil iam ch serviceAccount:{service_account}:objectViewer gs://{BUCKET_NAME}'
    )
    if not success:
        print(f"⚠️  Warning: Failed to grant objectViewer role: {stderr}")
    else:
        print("   ✅ storage.objectViewer role granted")
    
    # Grant storage.objectCreator role
    print("   📥 Granting storage.objectCreator role...")
    success, stdout, stderr = run_command(
        f'gsutil iam ch serviceAccount:{service_account}:objectCreator gs://{BUCKET_NAME}'
    )
    if not success:
        print(f"⚠️  Warning: Failed to grant objectCreator role: {stderr}")
    else:
        print("   ✅ storage.objectCreator role granted")
    
    # Grant storage.legacyBucketReader role (for listing)
    print("   📋 Granting storage.legacyBucketReader role...")
    success, stdout, stderr = run_command(
        f'gsutil iam ch serviceAccount:{service_account}:legacyBucketReader gs://{BUCKET_NAME}'
    )
    if not success:
        print(f"⚠️  Warning: Failed to grant legacyBucketReader role: {stderr}")
    else:
        print("   ✅ storage.legacyBucketReader role granted")
    
    # Step 4: Verify permissions
    print("\n4️⃣ Verifying permissions...")
    success, stdout, stderr = run_command(
        f'gsutil iam get gs://{BUCKET_NAME}'
    )
    
    if success:
        print("✅ IAM permissions verified")
        print("\n📋 Current IAM bindings:")
        print(stdout)
    else:
        print(f"❌ Failed to verify permissions: {stderr}")
    
    # Step 5: Test bucket access
    print("\n5️⃣ Testing bucket access...")
    success, stdout, stderr = run_command(
        f'gsutil ls gs://{BUCKET_NAME}/'
    )
    
    if success:
        print("✅ Bucket access test successful")
    else:
        print(f"❌ Bucket access test failed: {stderr}")
    
    print("\n🎉 Setup complete!")
    print(f"📝 Service account: {service_account}")
    print(f"📝 Bucket: gs://{BUCKET_NAME}")
    print("\n💡 If you still get 500 errors, check the Cloud Run logs:")
    print(f"   gcloud run services logs read {SERVICE_NAME} --region={REGION} --project={PROJECT_ID}")

if __name__ == "__main__":
    main() 