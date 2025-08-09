#!/usr/bin/env python3
"""
Simple Apollo API test script
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_apollo_api():
    """Test Apollo API with minimal parameters"""
    api_key = os.getenv('APOLLO_API_KEY')
    if not api_key:
        print("❌ No Apollo API key found in .env file")
        return
    
    print(f"🔑 Testing Apollo API with key: {api_key[:10]}...")
    
    # Test the exact endpoint and parameters
    url = "https://api.apollo.io/v1/people/search"
    
    # Minimal test parameters (no API key in body)
    test_params = {
        "page": 1,
        "per_page": 2
    }
    
    # Headers with API key
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    print(f"📡 Testing URL: {url}")
    print(f"📋 Parameters: {test_params}")
    print(f"🔑 Headers: X-Api-Key: {api_key[:10]}...")
    
    try:
        response = requests.post(url, json=test_params, headers=headers, timeout=30)
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data.get('people', []))} people")
            if data.get('people'):
                print(f"   First person: {data['people'][0].get('name', 'Unknown')}")
        else:
            print(f"❌ Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_apollo_api()
