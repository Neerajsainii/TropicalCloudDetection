#!/usr/bin/env python3
"""
Test script to verify Google Cloud Storage connection and permissions
"""

import os
import sys
from datetime import timedelta

def test_gcs_connection():
    """Test Google Cloud Storage connection"""
    print("🧪 Testing Google Cloud Storage connection...")
    
    try:
        # Test if google-cloud-storage is available
        from google.cloud import storage
        print("✅ google-cloud-storage library is available")
        
        # Test client initialization
        print("🔧 Initializing storage client...")
        storage_client = storage.Client()
        print("✅ Storage client initialized successfully")
        
        # Test authentication
        print("🔐 Testing authentication...")
        try:
            # This will trigger authentication
            buckets = list(storage_client.list_buckets(max_results=1))
            print("✅ Authentication successful")
        except Exception as auth_error:
            print(f"❌ Authentication failed: {auth_error}")
            return False
        
        # Test bucket access
        bucket_name = "tropical-cloud-detection-uploads"
        print(f"📦 Testing access to bucket: {bucket_name}")
        
        bucket = storage_client.bucket(bucket_name)
        
        # Check if bucket exists
        if bucket.exists():
            print(f"✅ Bucket {bucket_name} exists")
        else:
            print(f"❌ Bucket {bucket_name} does not exist")
            return False
        
        # Test blob operations
        print("📝 Testing blob operations...")
        test_blob_name = "test_connection.txt"
        blob = bucket.blob(test_blob_name)
        
        # Test signed URL generation
        print("🔗 Testing signed URL generation...")
        try:
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=1),
                method="PUT",
                content_type="application/octet-stream"
            )
            print("✅ Signed URL generation successful")
            print(f"   URL: {signed_url[:50]}...")
        except Exception as url_error:
            print(f"❌ Signed URL generation failed: {url_error}")
            return False
        
        # Test file upload (small test file)
        print("📤 Testing file upload...")
        try:
            test_content = b"Test file for GCS connection"
            blob.upload_from_string(test_content, content_type="text/plain")
            print("✅ File upload successful")
            
            # Clean up test file
            blob.delete()
            print("✅ Test file cleaned up")
        except Exception as upload_error:
            print(f"❌ File upload failed: {upload_error}")
            return False
        
        print("\n🎉 All tests passed! Google Cloud Storage is properly configured.")
        return True
        
    except ImportError:
        print("❌ google-cloud-storage library not available")
        print("   Install it with: pip install google-cloud-storage")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Google Cloud Storage Connection Test")
    print("=" * 50)
    
    success = test_gcs_connection()
    
    if success:
        print("\n✅ All tests passed! Your GCS setup is working correctly.")
        print("💡 If you're still getting 500 errors in Cloud Run, check:")
        print("   1. Service account permissions")
        print("   2. Cloud Run logs for specific error messages")
        print("   3. Environment variables in Cloud Run")
    else:
        print("\n❌ Tests failed. Please check your GCS configuration.")
        print("💡 Common issues:")
        print("   1. Missing google-cloud-storage dependency")
        print("   2. Authentication credentials not set up")
        print("   3. Incorrect bucket name or permissions")

if __name__ == "__main__":
    main() 