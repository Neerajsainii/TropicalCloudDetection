#!/usr/bin/env python3
"""
Test script to verify the upload endpoint works
"""

import requests
import json
import sys

def test_upload_endpoint():
    """Test the upload endpoint"""
    base_url = "https://tropical-cloud-detection-1065844967286.us-central1.run.app"
    
    print("🧪 Testing upload endpoint...")
    print(f"📡 Base URL: {base_url}")
    
    # Test 1: Check if the page loads
    print("\n1️⃣ Testing page load...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Home page loads successfully")
        else:
            print(f"❌ Home page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to load home page: {e}")
        return False
    
    # Test 2: Test get-upload-url endpoint
    print("\n2️⃣ Testing get-upload-url endpoint...")
    try:
        response = requests.get(f"{base_url}/get-upload-url/")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ get-upload-url endpoint works!")
            print(f"📋 Response keys: {list(data.keys())}")
            
            # Check if we got the expected fields
            if 'upload_url' in data:
                print("✅ Upload URL received")
                print(f"🔗 URL starts with: {data['upload_url'][:50]}...")
            else:
                print("⚠️ No upload_url in response")
                if 'error' in data:
                    print(f"❌ Error: {data['error']}")
                if 'details' in data:
                    print(f"📝 Details: {data['details']}")
                if 'solution' in data:
                    print(f"💡 Solution: {data['solution']}")
                return False
                
            if 'filename' in data:
                print(f"📄 Filename: {data['filename']}")
            if 'bucket_name' in data:
                print(f"📦 Bucket: {data['bucket_name']}")
            if 'upload_method' in data:
                print(f"🚀 Method: {data['upload_method']}")
                
            return True
        else:
            print(f"❌ get-upload-url failed with status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📋 Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test get-upload-url: {e}")
        return False

def test_health_endpoint():
    """Test the health check endpoint"""
    base_url = "https://tropical-cloud-detection-1065844967286.us-central1.run.app"
    
    print("\n3️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health/")
        print(f"📊 Health check status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint works!")
            print(f"📋 Health data: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test health endpoint: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Upload Endpoint Test")
    print("=" * 50)
    
    # Test upload endpoint
    upload_success = test_upload_endpoint()
    
    # Test health endpoint
    health_success = test_health_endpoint()
    
    if upload_success and health_success:
        print("\n🎉 All tests passed!")
        print("✅ Your upload system is working correctly")
    elif upload_success:
        print("\n⚠️ Upload endpoint works but health check failed")
        print("💡 This might indicate a partial issue")
    else:
        print("\n❌ Upload endpoint has issues")
        print("💡 Common solutions:")
        print("   1. Check Cloud Run logs for errors")
        print("   2. Verify Google Cloud Storage permissions")
        print("   3. Ensure the bucket exists")
        print("   4. Check service account IAM roles")

if __name__ == "__main__":
    main() 