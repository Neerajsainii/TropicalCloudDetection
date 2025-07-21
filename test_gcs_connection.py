#!/usr/bin/env python3
"""
Test script to debug Google Cloud Storage connection issues
"""

import os
import sys
import logging
from datetime import timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_gcs_connection():
    """Test Google Cloud Storage connection and permissions"""
    print("🔍 Testing Google Cloud Storage Connection...")
    
    # Test 1: Check if google-cloud-storage is installed
    print("\n1️⃣ Checking google-cloud-storage library...")
    try:
        from google.cloud import storage
        print("✅ google-cloud-storage library is available")
    except ImportError as e:
        print(f"❌ google-cloud-storage library not available: {e}")
        print("💡 Install with: pip install google-cloud-storage")
        return False
    
    # Test 2: Check environment variables
    print("\n2️⃣ Checking environment variables...")
    bucket_name = os.environ.get('GCS_BUCKET_NAME', 'tropical-cloud-detection-uploads')
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'tropical-cloud-detection')
    service_account_key = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    print(f"📦 Bucket name: {bucket_name}")
    print(f"🏢 Project ID: {project_id}")
    print(f"🔑 Service account key: {service_account_key}")
    
    if service_account_key:
        if os.path.exists(service_account_key):
            print("✅ Service account key file exists")
        else:
            print("❌ Service account key file not found")
    else:
        print("ℹ️ No service account key specified, will use default credentials")
    
    # Test 3: Initialize storage client
    print("\n3️⃣ Initializing storage client...")
    try:
        if service_account_key and os.path.exists(service_account_key):
            print("🔑 Using service account key for authentication...")
            storage_client = storage.Client.from_service_account_json(service_account_key)
        else:
            print("🔐 Using default credentials...")
            storage_client = storage.Client()
        
        print("✅ Storage client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize storage client: {e}")
        return False
    
    # Test 4: Test authentication
    print("\n4️⃣ Testing authentication...")
    try:
        # This will trigger authentication and permission checks
        buckets = list(storage_client.list_buckets(max_results=1))
        print("✅ Authentication successful")
        print(f"📋 Found {len(buckets)} bucket(s) accessible")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("💡 Check if service account has proper IAM permissions")
        return False
    
    # Test 5: Check bucket access
    print(f"\n5️⃣ Checking bucket access: {bucket_name}")
    try:
        bucket = storage_client.bucket(bucket_name)
        
        if bucket.exists():
            print("✅ Bucket exists and is accessible")
        else:
            print(f"❌ Bucket {bucket_name} does not exist")
            print(f"💡 Create bucket '{bucket_name}' in Google Cloud Console")
            return False
            
    except Exception as e:
        print(f"❌ Failed to access bucket {bucket_name}: {e}")
        return False
    
    # Test 6: Test signed URL generation
    print("\n6️⃣ Testing signed URL generation...")
    try:
        import uuid
        test_filename = f"test_file_{uuid.uuid4()}.txt"
        blob = bucket.blob(test_filename)
        
        # Generate signed URL for upload
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(hours=1),
            method="PUT",
            content_type="application/octet-stream"
        )
        
        print("✅ Signed URL generation successful")
        print(f"🔗 Generated URL: {url[:50]}...")
        
        # Clean up test blob
        blob.delete()
        print("🧹 Cleaned up test blob")
        
    except Exception as e:
        print(f"❌ Signed URL generation failed: {e}")
        print("💡 Check if service account has 'Storage Object Creator' role")
        return False
    
    print("\n🎉 All tests passed! Google Cloud Storage is properly configured.")
    return True

def main():
    """Main function"""
    print("🚀 Google Cloud Storage Connection Test")
    print("=" * 50)
    
    success = test_gcs_connection()
    
    if success:
        print("\n✅ Your Google Cloud Storage setup is working correctly!")
        print("💡 The upload issues might be related to:")
        print("   - Network connectivity")
        print("   - File size limits")
        print("   - Browser CORS issues")
    else:
        print("\n❌ Google Cloud Storage setup has issues.")
        print("💡 Common solutions:")
        print("   1. Grant IAM roles to service account:")
        print("      - Storage Object Viewer")
        print("      - Storage Object Creator")
        print("   2. Create the bucket if it doesn't exist")
        print("   3. Check service account key file")
        print("   4. Verify project ID is correct")

if __name__ == "__main__":
    main() 