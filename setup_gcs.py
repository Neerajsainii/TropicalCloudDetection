#!/usr/bin/env python3
"""
Setup script for Google Cloud Storage bucket and permissions
Run this script to create the necessary GCS bucket for large file uploads
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None

def setup_gcs_bucket():
    """Set up Google Cloud Storage bucket for file uploads"""
    
    project_id = "tropical-cloud-detection"
    bucket_name = "tropical-cloud-detection-uploads"
    region = "us-central1"
    
    print("🚀 Setting up Google Cloud Storage for large file uploads...")
    
    # 1. Create the bucket
    print(f"📦 Creating bucket: {bucket_name}")
    create_bucket_cmd = f"gsutil mb -p {project_id} -c STANDARD -l {region} gs://{bucket_name}"
    result = run_command(create_bucket_cmd)
    
    if result is None:
        print("❌ Failed to create bucket. It might already exist.")
    else:
        print(f"✅ Bucket created: {bucket_name}")
    
    # 2. Set bucket permissions for Cloud Run service account
    print("🔐 Setting bucket permissions...")
    
    # Get the Cloud Run service account
    service_account = f"{project_id}@appspot.gserviceaccount.com"
    
    # Make bucket publicly readable (for signed URLs to work)
    make_public_cmd = f"gsutil iam ch allUsers:objectViewer gs://{bucket_name}"
    run_command(make_public_cmd)
    
    # 3. Set lifecycle policy to delete old files (optional)
    print("🗑️ Setting lifecycle policy...")
    lifecycle_config = f"""
{{
  "rule": [
    {{
      "action": {{"type": "Delete"}},
      "condition": {{
        "age": 30,
        "isLive": true
      }}
    }}
  ]
}}
"""
    
    with open("lifecycle.json", "w") as f:
        f.write(lifecycle_config)
    
    lifecycle_cmd = f"gsutil lifecycle set lifecycle.json gs://{bucket_name}"
    run_command(lifecycle_cmd)
    
    # Clean up
    os.remove("lifecycle.json")
    
    print("✅ Google Cloud Storage setup complete!")
    print(f"📁 Bucket: gs://{bucket_name}")
    print(f"🌍 Region: {region}")
    print(f"📊 Files will be automatically deleted after 30 days")
    
    return bucket_name

def update_environment_variables():
    """Update environment variables to include GCS bucket name"""
    
    bucket_name = "tropical-cloud-detection-uploads"
    
    # Read current env_vars.yaml
    try:
        with open("env_vars.yaml", "r") as f:
            content = f.read()
    except FileNotFoundError:
        content = ""
    
    # Add GCS bucket name if not already present
    if "GCS_BUCKET_NAME" not in content:
        with open("env_vars.yaml", "a") as f:
            f.write(f"\nGCS_BUCKET_NAME: {bucket_name}\n")
        print(f"✅ Added GCS_BUCKET_NAME to env_vars.yaml")
    else:
        print("ℹ️ GCS_BUCKET_NAME already in env_vars.yaml")

if __name__ == "__main__":
    print("🔧 Setting up Google Cloud Storage for Tropical Cloud Detection")
    print("=" * 60)
    
    # Check if gcloud is authenticated
    auth_check = run_command("gcloud auth list --filter=status:ACTIVE --format='value(account)'")
    if not auth_check:
        print("❌ Please authenticate with gcloud first:")
        print("   gcloud auth login")
        sys.exit(1)
    
    print(f"✅ Authenticated as: {auth_check}")
    
    # Set up GCS bucket
    bucket_name = setup_gcs_bucket()
    
    # Update environment variables
    update_environment_variables()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Rebuild and redeploy your Docker image")
    print("2. Update your Cloud Run service with the new environment variables")
    print("3. Test uploading a large file (>32MB)")
    
    print(f"\n📁 Your files will be stored in: gs://{bucket_name}")
    print("🔗 You can view files in the Google Cloud Console") 