import requests
import time
from typing import List, Dict, Any
from config import Config


class AirtableAPI:
    """Handles interactions with Airtable API for storing lead data"""
    
    def __init__(self):
        self.api_key = Config.AIRTABLE_API_KEY
        self.base_id = Config.AIRTABLE_BASE_ID
        self.table_name = Config.AIRTABLE_TABLE_NAME
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_headers(self) -> Dict[str, str]:
        """Create headers for Airtable API requests"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def prepare_data_for_airtable(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare lead data for Airtable format"""
        records = []
        
        for lead in leads:
            record = {
                'fields': {
                    'Name': f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip(),
                    'Email': lead.get('email', ''),
                    'Job Title': lead.get('title', ''),
                    'Company': lead.get('company_name', ''),
                    'Company Size': lead.get('company_size', 0),
                    'Industry': lead.get('company_industry', ''),
                    'Region': lead.get('region', ''),
                    'Score': lead.get('score', 0),
                    'LinkedIn URL': lead.get('linkedin_url', ''),
                    'Phone': lead.get('phone', ''),
                    'Location': lead.get('location', ''),
                    'Processed Date': time.strftime('%Y-%m-%d'),
                    'Status': 'New Lead'
                }
            }
            records.append(record)
        
        return records
    
    def clear_table(self) -> bool:
        """Clear all records from the Airtable table"""
        try:
            # First, get all existing records
            response = requests.get(
                f"{self.base_url}/{self.table_name}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [])
                
                # Delete all records
                for record in records:
                    delete_response = requests.delete(
                        f"{self.base_url}/{self.table_name}/{record['id']}",
                        headers=self.headers
                    )
                    if delete_response.status_code != 200:
                        print(f"Warning: Failed to delete record {record['id']}")
                    time.sleep(0.1)  # Rate limiting
                
                print(f"Cleared {len(records)} existing records from Airtable")
                return True
            else:
                print(f"Failed to fetch existing records: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error clearing Airtable table: {e}")
            return False
    
    def write_leads_to_airtable(self, leads: List[Dict[str, Any]]) -> bool:
        """Write leads to Airtable in batches"""
        try:
            records = self.prepare_data_for_airtable(leads)
            
            # Airtable has a limit of 10 records per request
            batch_size = 10
            success_count = 0
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                
                payload = {
                    'records': batch
                }
                
                response = requests.post(
                    f"{self.base_url}/{self.table_name}",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    success_count += len(batch)
                    print(f"Successfully wrote batch of {len(batch)} records to Airtable")
                else:
                    print(f"Failed to write batch to Airtable: {response.status_code} - {response.text}")
                
                time.sleep(0.2)  # Rate limiting
            
            print(f"Total records written to Airtable: {success_count}")
            return success_count == len(records)
            
        except Exception as e:
            print(f"Error writing leads to Airtable: {e}")
            return False
    
    def push_leads(self, leads: List[Dict[str, Any]], clear_existing: bool = True) -> bool:
        """Main method to push leads to Airtable"""
        try:
            if not leads:
                print("No leads to push to Airtable")
                return True
            
            print(f"Pushing {len(leads)} leads to Airtable...")
            
            # Clear existing records if requested
            if clear_existing:
                if not self.clear_table():
                    print("Warning: Failed to clear existing records, continuing anyway...")
            
            # Write new leads
            success = self.write_leads_to_airtable(leads)
            
            if success:
                print(f"Successfully pushed {len(leads)} leads to Airtable")
            else:
                print("Failed to push some leads to Airtable")
            
            return success
            
        except Exception as e:
            print(f"Error in push_leads: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test the connection to Airtable"""
        try:
            response = requests.get(
                f"{self.base_url}/{self.table_name}?maxRecords=1",
                headers=self.headers
            )
            
            if response.status_code == 200:
                print("Airtable connection successful")
                return True
            else:
                print(f"Airtable connection failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error testing Airtable connection: {e}")
            return False
