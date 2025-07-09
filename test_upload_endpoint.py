#!/usr/bin/env python3
"""
Test script to verify the upload endpoint works
"""

import requests
import json

def test_upload_endpoint():
    """Test the upload endpoint"""
    base_url = "https://tropical-cloud-detection-1065844967286.us-central1.run.app"
    
    print("🧪 Testing upload endpoint...")
    print(f"📡 Base URL: {base_url}")
    
    # Test 1: Check if the page loads
    print("\n1️⃣ Testing page load...")
    try:
        response = requests.get(f"{base_url}/upload-large/")
        if response.status_code == 200:
            print("✅ Upload page loads successfully")
        else:
            print(f"❌ Upload page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to load upload page: {e}")
        return False
    
    # Test 2: Test get-upload-url endpoint
    print("\n2️⃣ Testing get-upload-url endpoint...")
    try:
        response = requests.get(f"{base_url}/get-upload-url/")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ get-upload-url endpoint works!")
            print(f"📋 Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ get-upload-url failed with status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📋 Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test get-upload-url: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Upload Endpoint Test")
    print("=" * 50)
    
    success = test_upload_endpoint()
    
    if success:
        print("\n🎉 All tests passed! The upload functionality should work correctly.")
        print("💡 You can now upload large files through the web interface.")
    else:
        print("\n❌ Tests failed. Please check the manual fix steps in MANUAL_GCS_FIX.md")
        print("💡 The most common issue is missing IAM permissions for Google Cloud Storage.")

if __name__ == "__main__":
    main() 