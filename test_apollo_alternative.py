#!/usr/bin/env python3
"""
Test Working Apollo Endpoints
Only tests endpoints that actually work for the MVP
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_working_endpoints():
    """Test only the working Apollo endpoints"""
    api_key = os.getenv('APOLLO_API_KEY')
    if not api_key:
        print("❌ No Apollo API key found in .env file")
        return
    
    print(f"🔑 Testing Working Apollo Endpoints with key: {api_key[:10]}...")
    
    # Headers with API key
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    # Test only the working endpoints
    endpoints = [
        {
            'name': 'Contacts Search (Contact Records)',
            'url': 'https://api.apollo.io/v1/contacts/search',
            'method': 'POST',
            'data': {'page': 1, 'per_page': 1}
        },
        {
            'name': 'Organization Search',
            'url': 'https://api.apollo.io/v1/organizations/search',
            'method': 'POST',
            'data': {'page': 1, 'per_page': 1}
        },
        {
            'name': 'Organization Enrichment',
            'url': 'https://api.apollo.io/v1/organizations/enrich',
            'method': 'POST',
            'data': {'domain': 'stripe.com'}
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        
        try:
            if endpoint['method'] == 'POST':
                response = requests.post(
                    endpoint['url'], 
                    json=endpoint['data'], 
                    headers=headers, 
                    timeout=30
                )
            else:
                response = requests.get(
                    endpoint['url'], 
                    params=endpoint['data'], 
                    headers=headers, 
                    timeout=30
                )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Response keys: {list(data.keys())}")
            else:
                print(f"   ❌ Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    print("\n🎯 These are your working endpoints for the MVP pipeline!")

if __name__ == "__main__":
    test_working_endpoints()
