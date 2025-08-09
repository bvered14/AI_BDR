#!/usr/bin/env python3
"""
Find Companies with Contacts
Quick test to find companies that actually have contacts in Apollo
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def find_companies_with_contacts():
    """Find companies that have contacts in Apollo"""
    api_key = os.getenv('APOLLO_API_KEY')
    if not api_key:
        print("❌ No Apollo API key found in .env file")
        return
    
    print(f"🔑 Finding Companies with Contacts using key: {api_key[:10]}...")
    
    # Headers with API key
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    print("\n🔍 Testing Different Company Types for Contacts")
    print("=" * 60)
    
    # Test different company types
    test_companies = [
        "linear.app",      # Popular tech company
        "vercel.com",      # Popular tech company  
        "figma.com",       # Popular tech company
        "github.com",      # Very popular tech company
        "slack.com"        # Popular tech company
    ]
    
    companies_with_contacts = []
    
    for domain in test_companies:
        print(f"\n🏢 Testing: {domain}")
        
        # Search for contacts at this company
        contact_params = {
            "page": 1,
            "per_page": 2,
            "q_organization_domains": [domain]
        }
        
        try:
            response = requests.post(
                'https://api.apollo.io/v1/contacts/search',
                json=contact_params,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get('contacts', [])
                print(f"   📊 Found {len(contacts)} contacts")
                
                if contacts:
                    companies_with_contacts.append(domain)
                    print(f"   ✅ SUCCESS! This company has contacts")
                    for i, contact in enumerate(contacts[:2], 1):
                        print(f"      👤 {contact.get('first_name', '')} {contact.get('last_name', '')} - {contact.get('title', 'Unknown')}")
                else:
                    print(f"   ⚠️  No contacts found")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    print(f"\n🎯 RESULTS:")
    print("=" * 60)
    if companies_with_contacts:
        print(f"✅ Found {len(companies_with_contacts)} companies with contacts:")
        for company in companies_with_contacts:
            print(f"   🏢 {company}")
        print(f"\n🚀 These are perfect for testing your full pipeline!")
    else:
        print("❌ No companies found with contacts")
        print("💡 We may need to adjust our search strategy")

if __name__ == "__main__":
    find_companies_with_contacts()
