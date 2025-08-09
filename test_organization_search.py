#!/usr/bin/env python3
"""
Test Apollo Organization Search
Since people search isn't available, let's see what company data we can get
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_organization_search():
    """Test Apollo organization search"""
    api_key = os.getenv('APOLLO_API_KEY')
    if not api_key:
        print("❌ No Apollo API key found in .env file")
        return
    
    print(f"🔑 Testing Apollo Organization Search with key: {api_key[:10]}...")
    
    # Headers with API key
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    # Test organization search with tech companies
    search_params = {
        "page": 1,
        "per_page": 3,
        "q_organization_domains": ["techflow.com", "datasync.io", "cloudscale.net"],
        "q_organization_size_ranges": ["11-50", "51-200"],
        "q_organization_industries": ["Technology", "Software"]
    }
    
    url = "https://api.apollo.io/v1/organizations/search"
    
    print(f"🔍 Searching for tech companies...")
    print(f"   Parameters: {search_params}")
    
    try:
        response = requests.post(url, json=search_params, headers=headers, timeout=30)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data.get('organizations', []))} organizations")
            
            # Show the organizations we found
            organizations = data.get('organizations', [])
            for i, org in enumerate(organizations[:3], 1):
                print(f"\n🏢 Organization {i}:")
                print(f"   Name: {org.get('name', 'Unknown')}")
                print(f"   Domain: {org.get('domain', 'Unknown')}")
                print(f"   Size: {org.get('size_range', 'Unknown')}")
                print(f"   Industry: {org.get('industry', 'Unknown')}")
                print(f"   Location: {org.get('location', 'Unknown')}")
                
                # Check if we have employee info
                if 'employees_ranges' in org:
                    print(f"   Employees: {org['employees_ranges']}")
                
        else:
            print(f"❌ Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_organization_search()
