#!/usr/bin/env python3
"""
Test Existing Pipeline
Tests AI enrichment and Airtable pipeline without fetching new Apollo leads
"""
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from process_leads import LeadProcessor
    from outreach import OutreachGenerator
    from airtable_api import AirtableAPI
    from config import Config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

# Load environment variables
load_dotenv()

def test_existing_pipeline():
    """Test the pipeline with existing data"""
    print("🚀 Testing Existing Pipeline (AI + Airtable)")
    print("=" * 50)
    
    # Validate configuration
    try:
        Config.validate_required()
        print("✅ Configuration validated")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Test Airtable connection
    print("\n🔍 Testing Airtable connection...")
    try:
        airtable = AirtableAPI()
        airtable.test_connection()
        print("✅ Airtable connection successful")
    except Exception as e:
        print(f"❌ Airtable connection failed: {e}")
        return
    
    # Test AI enrichment (without Apollo data)
    print("\n🤖 Testing AI enrichment...")
    try:
        processor = LeadProcessor()
        print("✅ Lead processor initialized")
        
        # Test with sample data
        sample_lead = {
            'first_name': 'John',
            'last_name': 'Doe',
            'title': 'CTO',
            'company_name': 'Test Company',
            'company_industry': 'Technology',
            'company_size': 200,
            'region': 'North America'
        }
        
        print(f"   📝 Testing with sample lead: {sample_lead['first_name']} {sample_lead['last_name']}")
        
        # Test scoring
        score, reasons = processor.calculate_total_score(sample_lead)
        print(f"   🎯 Score: {score:.2f}")
        print(f"   📊 Reasons: {reasons}")
        
        # Test email generation
        email_gen = OutreachGenerator()
        email_data = email_gen.generate_personalized_email(sample_lead)
        print(f"   📧 Email generated: {len(email_data.get('body', ''))} characters")
        print(f"   📋 Subject: {email_data.get('subject', 'No subject')}")
        print(f"   📋 Preview: {email_data.get('body', '')[:100]}...")
        
        print("✅ AI enrichment working")
        
    except Exception as e:
        print(f"❌ AI enrichment failed: {e}")
        return
    
    print("\n🎯 Pipeline Test Results:")
    print("=" * 50)
    print("✅ Configuration: Working")
    print("✅ Airtable: Working")
    print("✅ AI Enrichment: Working")
    print("✅ Email Generation: Working")
    print("\n🚀 Your pipeline is ready for the next step!")
    print("💡 Next: Use your existing Apollo list data to test the full flow")

if __name__ == "__main__":
    test_existing_pipeline()
