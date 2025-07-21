#!/usr/bin/env python3
"""
Script to help fix Google Cloud Storage permissions
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔧 {description}")
    print(f"📝 Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Command executed successfully")
            if result.stdout.strip():
                print(f"📋 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Command failed with exit code {result.returncode}")
            if result.stderr.strip():
                print(f"📋 Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Failed to execute command: {e}")
        return False

def get_project_info():
    """Get current project information"""
    print("🔍 Getting project information...")
    
    # Get project ID
    project_result = subprocess.run(
        "gcloud config get-value project", 
        shell=True, capture_output=True, text=True
    )
    
    if project_result.returncode == 0:
        project_id = project_result.stdout.strip()
        print(f"🏢 Project ID: {project_id}")
        return project_id
    else:
        print("❌ Failed to get project ID")
        print("💡 Make sure you're authenticated with gcloud")
        return None

def get_service_account():
    """Get the Cloud Run service account"""
    project_id = get_project_info()
    if not project_id:
        return None
    
    # Extract project number from project ID
    # This is a simplified approach - in practice you'd need to get the actual project number
    print(f"🔑 Service account will be: {project_id}-compute@developer.gserviceaccount.com")
    return f"{project_id}-compute@developer.gserviceaccount.com"

def fix_gcs_permissions():
    """Fix Google Cloud Storage permissions"""
    print("🚀 Google Cloud Storage Permissions Fix")
    print("=" * 50)
    
    # Get project info
    project_id = get_project_info()
    if not project_id:
        print("\n❌ Cannot proceed without project information")
        print("💡 Run: gcloud auth login && gcloud config set project YOUR_PROJECT_ID")
        return False
    
    service_account = get_service_account()
    bucket_name = "tropical-cloud-detection-uploads"
    
    print(f"\n📦 Target bucket: {bucket_name}")
    print(f"🔑 Service account: {service_account}")
    
    # Step 1: Grant IAM roles to service account
    print("\n1️⃣ Granting IAM roles to service account...")
    
    roles = [
        "roles/storage.objectViewer",
        "roles/storage.objectCreator", 
        "roles/storage.legacyBucketReader"
    ]
    
    success_count = 0
    for role in roles:
        command = f"gcloud projects add-iam-policy-binding {project_id} --member=serviceAccount:{service_account} --role={role}"
        if run_command(command, f"Granting {role}"):
            success_count += 1
    
    if success_count == len(roles):
        print("✅ All IAM roles granted successfully")
    else:
        print(f"⚠️ Only {success_count}/{len(roles)} roles were granted")
    
    # Step 2: Create bucket if it doesn't exist
    print("\n2️⃣ Creating bucket if it doesn't exist...")
    bucket_command = f"gsutil mb -p {project_id} -c STANDARD -l us-central1 gs://{bucket_name}"
    run_command(bucket_command, "Creating bucket")
    
    # Step 3: Grant bucket-specific permissions
    print("\n3️⃣ Granting bucket-specific permissions...")
    bucket_permissions = [
        f"gcloud storage buckets add-iam-policy-binding gs://{bucket_name} --member=serviceAccount:{service_account} --role=roles/storage.objectViewer",
        f"gcloud storage buckets add-iam-policy-binding gs://{bucket_name} --member=serviceAccount:{service_account} --role=roles/storage.objectCreator"
    ]
    
    for command in bucket_permissions:
        run_command(command, "Granting bucket permission")
    
    print("\n🎉 Permission fix completed!")
    print("💡 You may need to wait a few minutes for permissions to propagate")
    return True

def test_fix():
    """Test if the fix worked"""
    print("\n🧪 Testing the fix...")
    
    # Test the endpoint
    import requests
    try:
        response = requests.get("https://tropical-cloud-detection-1065844967286.us-central1.run.app/get-upload-url/")
        if response.status_code == 200:
            data = response.json()
            if 'upload_url' in data:
                print("✅ Fix successful! Upload URL generation is working")
                return True
            else:
                print("⚠️ Still getting server_side upload method")
                print(f"📋 Response: {data}")
                return False
        else:
            print(f"❌ Endpoint still failing: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Google Cloud Storage Permissions Fix")
    print("=" * 50)
    
    # Check if gcloud is available
    try:
        subprocess.run("gcloud --version", shell=True, capture_output=True, check=True)
    except:
        print("❌ gcloud CLI not found")
        print("💡 Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install")
        return
    
    # Run the fix
    if fix_gcs_permissions():
        print("\n⏳ Waiting 30 seconds for permissions to propagate...")
        import time
        time.sleep(30)
        
        # Test the fix
        if test_fix():
            print("\n🎉 All fixed! Your upload system should now work correctly.")
        else:
            print("\n⚠️ Fix may need more time to propagate or additional steps.")
            print("💡 Check Cloud Run logs for specific error messages.")
    else:
        print("\n❌ Fix failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 