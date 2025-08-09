#!/usr/bin/env python3
"""
Check Airtable Data
Simple script to see what's currently in your Airtable tables
"""
import os
import sys
from dotenv import load_dotenv
import requests

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from airtable_api import AirtableAPI
    from config import Config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

# Load environment variables
load_dotenv()

def check_airtable_data():
    """Check what data is in your Airtable tables"""
    print("🔍 Checking Airtable Data")
    print("=" * 50)
    
    try:
        # Test connection first
        airtable = AirtableAPI()
        airtable.test_connection()
        
        # Get table names
        table_names = airtable.get_table_names()
        print(f"📋 Available tables: {table_names}")
        
        # Check each table
        for table_name in table_names:
            print(f"\n📊 Table: {table_name}")
            print("-" * 30)
            
            # Create a new instance for each table
            table_api = AirtableAPI(table_name)
            
            # Try to get records from this table
            try:
                response = requests.get(
                    f"{table_api.base_url}/{table_name}",
                    headers=table_api.headers,
                    params={'maxRecords': 10}  # Limit to 10 records for preview
                )
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get('records', [])
                    print(f"   Found {len(records)} records")
                    
                    if records:
                        print("   Sample records:")
                        for i, record in enumerate(records[:3], 1):  # Show first 3
                            fields = record.get('fields', {})
                            print(f"   {i}. ID: {record.get('id', 'N/A')}")
                            for key, value in fields.items():
                                if isinstance(value, str) and len(value) > 50:
                                    value = value[:50] + "..."
                                print(f"      {key}: {value}")
                            print()
                    else:
                        print("   No records found")
                else:
                    print(f"   ❌ Error: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error accessing table: {e}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_airtable_data()
