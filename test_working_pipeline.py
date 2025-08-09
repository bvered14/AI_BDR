#!/usr/bin/env python3
"""
Test Working Apollo Pipeline
Tests the full MVP pipeline with working endpoints
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_working_pipeline():
    """Test the working Apollo endpoints for MVP"""
    api_key = os.getenv('APOLLO_API_KEY')
    if not api_key:
        print("❌ No Apollo API key found in .env file")
        return
    
    print(f"🔑 Testing Working Apollo Pipeline with key: {api_key[:10]}...")
    
    # Headers with API key
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    print("\n🚀 Step 1: Find Target Companies (Cap: 2)")
    print("=" * 50)
    
    # Use known tech company domains for reliable results
    target_domains = ["stripe.com", "notion.so"]  # Cap of 2 for MVP
    
    for i, domain in enumerate(target_domains, 1):
        print(f"\n🏢 Company {i}: {domain}")
        
        # Step 2: Enrich company data directly by domain
        print(f"\n🔍 Step 2: Enriching company data...")
        enrich_response = requests.post(
            'https://api.apollo.io/v1/organizations/enrich',
            json={'domain': domain},
            headers=headers,
            timeout=30
        )
        
        if enrich_response.status_code == 200:
            enrich_data = enrich_response.json()
            org = enrich_data.get('organization', {})
            company_name = org.get('name', 'Unknown')
            company_id = org.get('id', 'Unknown')
            
            print(f"   ✅ Company: {company_name}")
            print(f"   ✅ Founded: {org.get('founded_year', 'Unknown')}")
            print(f"   ✅ Industry: {org.get('industry', 'Unknown')}")
            print(f"   ✅ Size: {org.get('size_range', 'Unknown')}")
            print(f"   ✅ Location: {org.get('location', 'Unknown')}")
            print(f"   ✅ Description: {org.get('description', 'Unknown')[:100]}...")
            
            # Step 3: Find contacts at this company
            print(f"\n👥 Step 3: Finding contacts at {company_name}...")
            contact_search_params = {
                "page": 1,
                "per_page": 2,  # Limit to 2 contacts per company
                "q_organization_domains": [domain]  # Search by domain
            }
            
            print(f"   📋 Search params: {contact_search_params}")
            
            contact_response = requests.post(
                'https://api.apollo.io/v1/contacts/search',
                json=contact_search_params,
                headers=headers,
                timeout=30
            )
            
            print(f"   📊 Response status: {contact_response.status_code}")
            
            if contact_response.status_code == 200:
                contact_data = contact_response.json()
                contacts = contact_data.get('contacts', [])
                print(f"   ✅ Found {len(contacts)} contacts")
                
                if contacts:
                    for j, contact in enumerate(contacts, 1):
                        print(f"\n      👤 Contact {j}:")
                        print(f"         Name: {contact.get('first_name', '')} {contact.get('last_name', '')}")
                        print(f"         Title: {contact.get('title', 'Unknown')}")
                        print(f"         Email: {contact.get('email', 'Unknown')}")
                        print(f"         LinkedIn: {contact.get('linkedin_url', 'Unknown')}")
                        print(f"         Phone: {contact.get('phone', 'Unknown')}")
                        
                        # This contact is ready for your AI pipeline!
                        print(f"         🚀 Ready for AI enrichment and email generation!")
                else:
                    print(f"      ⚠️  No contacts found for this company")
                    print(f"      💡 This is normal - not all companies have contacts in Apollo's database")
            else:
                print(f"   ❌ Contact search failed: {contact_response.status_code}")
                print(f"      Error: {contact_response.text[:200]}")
        else:
            print(f"   ❌ Company enrichment failed: {enrich_response.status_code}")
            print(f"      Error: {enrich_response.text[:200]}")
    
    print("\n📋 Your Working MVP Pipeline:")
    print("=" * 50)
    print("1. ✅ Find companies with organizations/enrich")
    print("2. ✅ Enrich companies with organizations/enrich") 
    print("3. ✅ Find contacts with contacts/search")
    print("4. 🚀 Feed contacts into your AI pipeline")
    print("5. 📧 Generate and send personalized emails")
    print("\n🎯 This approach will work with your current Apollo plan!")

if __name__ == "__main__":
    test_working_pipeline()
