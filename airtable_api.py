import requests
import time
from typing import List, Dict, Any, Optional
from config import Config


class AirtableAPI:
    """Handles interactions with Airtable API for storing lead data"""
    
    def __init__(self, table_name: Optional[str] = None):
        self.api_key = Config.AIRTABLE_API_KEY
        self.base_id = Config.AIRTABLE_BASE_ID
        self.table_name = table_name or Config.AIRTABLE_TABLE_NAME
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
    
    def find_existing_record(self, email: str, company_name: str = None) -> Optional[str]:
        """
        Find existing record by email (primary) or name + company (fallback)
        Returns record ID if found, None otherwise
        """
        try:
            # First try to find by email
            if email:
                filter_formula = f"{{Email}} = '{email}'"
                response = requests.get(
                    f"{self.base_url}/{self.table_name}",
                    headers=self.headers,
                    params={'filterByFormula': filter_formula}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('records'):
                        return data['records'][0]['id']
            
            # Fallback: try to find by name + company
            if company_name:
                name_field = f"{{Name}} = '{company_name}'"
                response = requests.get(
                    f"{self.base_url}/{self.table_name}",
                    headers=self.headers,
                    params={'filterByFormula': name_field}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('records'):
                        return data['records'][0]['id']
            
            return None
            
        except Exception as e:
            print(f"Error finding existing record: {e}")
            return None
    
    def upsert_record(self, record_data: Dict[str, Any]) -> bool:
        """
        Upsert a record - update if exists, create if not
        """
        try:
            email = record_data['fields'].get('Email', '')
            company_name = record_data['fields'].get('Company', '')
            
            # Check if record exists
            existing_id = self.find_existing_record(email, company_name)
            
            if existing_id:
                # Update existing record
                response = requests.patch(
                    f"{self.base_url}/{self.table_name}/{existing_id}",
                    headers=self.headers,
                    json=record_data
                )
                if response.status_code == 200:
                    print(f"✅ Updated existing record: {email or company_name}")
                    return True
                else:
                    print(f"❌ Failed to update record: {response.status_code}")
                    return False
            else:
                # Create new record
                response = requests.post(
                    f"{self.base_url}/{self.table_name}",
                    headers=self.headers,
                    json=record_data
                )
                if response.status_code == 200:
                    print(f"✅ Created new record: {email or company_name}")
                    return True
                else:
                    print(f"❌ Failed to create record: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"Error upserting record: {e}")
            return False
    
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
                    'Score Reasons': ', '.join(lead.get('score_reasons', [])),
                    'LinkedIn URL': lead.get('linkedin_url', ''),
                    'Phone': lead.get('phone', ''),
                    'Location': lead.get('location', ''),
                    'Processed Date': time.strftime('%Y-%m-%d'),
                    'Status': 'New Lead',
                    'Outreach Message': lead.get('outreach_message', '')
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
        """Write leads to Airtable using upsert to prevent duplicates"""
        try:
            records = self.prepare_data_for_airtable(leads)
            
            success_count = 0
            total_count = len(records)
            
            for record in records:
                if self.upsert_record(record):
                    success_count += 1
                time.sleep(0.1)  # Rate limiting
            
            print(f"✅ Successfully upserted {success_count}/{total_count} leads to Airtable")
            return success_count == total_count
                
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
