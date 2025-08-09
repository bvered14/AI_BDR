#!/usr/bin/env python3
"""
Test script for Apollo API caching system
=========================================

This script tests the caching functionality without making actual API calls.
"""

import json
import pathlib
import time
from apollo_api import ApolloAPI

def test_cache_functionality():
    """Test the caching system functionality"""
    print("🧪 Testing Apollo API Caching System")
    print("=" * 50)
    
    # Create Apollo API instance
    apollo = ApolloAPI()
    
    # Test 1: Check initial cache status
    print("\n1. Initial cache status:")
    apollo.print_cache_status()
    
    # Test 2: Create mock data and cache it
    print("\n2. Creating mock data and caching...")
    mock_leads = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@test.com",
            "title": "CTO",
            "company_name": "Test Corp",
            "company_size": 150,
            "company_industry": "Software",
            "company_location": "San Francisco, CA",
            "linkedin_url": "https://linkedin.com/in/johndoe",
            "apollo_id": "test_1",
            "company_domain": "testcorp.com",
            "company_revenue": "$10M-50M",
            "company_founded": "2015",
            "region": "North America"
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@test.com",
            "title": "Head of Security",
            "company_name": "SecureTest",
            "company_size": 75,
            "company_industry": "Cybersecurity",
            "company_location": "London, UK",
            "linkedin_url": "https://linkedin.com/in/janesmith",
            "apollo_id": "test_2",
            "company_domain": "securetest.com",
            "company_revenue": "$5M-10M",
            "company_founded": "2018",
            "region": "Europe"
        }
    ]
    
    # Save to cache
    apollo._save_to_cache(mock_leads)
    
    # Test 3: Check cache status after saving
    print("\n3. Cache status after saving mock data:")
    apollo.print_cache_status()
    
    # Test 4: Load from cache
    print("\n4. Loading from cache:")
    loaded_leads = apollo._load_from_cache()
    print(f"   Loaded {len(loaded_leads)} leads from cache")
    
    # Test 5: Test cache expiry
    print("\n5. Testing cache expiry...")
    # Temporarily set expiry to 1 second for testing
    original_expiry = apollo.cache_expiry_hours
    apollo.cache_expiry_hours = 1/3600  # 1 second
    
    # Wait a moment
    time.sleep(1.1)
    
    # Check if cache is expired
    is_valid = apollo._is_cache_valid()
    print(f"   Cache valid after 1 second: {is_valid}")
    
    # Restore original expiry
    apollo.cache_expiry_hours = original_expiry
    
    # Test 6: Cache settings
    print("\n6. Testing cache settings:")
    apollo.set_cache_settings(enabled=True, expiry_hours=48)
    
    # Test 7: Final cache status
    print("\n7. Final cache status:")
    apollo.print_cache_status()
    
    print("\n✅ Cache testing completed!")

def test_cache_commands():
    """Test the cache management commands"""
    print("\n🔧 Testing Cache Management Commands")
    print("=" * 50)
    
    apollo = ApolloAPI()
    
    # Test cache info
    print("\nCache info:")
    cache_info = apollo.get_cache_info()
    for key, value in cache_info.items():
        print(f"  {key}: {value}")
    
    # Test cache settings
    print("\nCache settings:")
    apollo.set_cache_settings(enabled=False)
    apollo.set_cache_settings(enabled=True, expiry_hours=12)

if __name__ == "__main__":
    try:
        test_cache_functionality()
        test_cache_commands()
        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
