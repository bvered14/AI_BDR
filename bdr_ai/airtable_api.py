import requests
import time
from typing import List, Dict, Any, Optional
from .config import Config


class AirtableAPI:
    """Handles interactions with Airtable API for storing lead data"""
    
    def __init__(self, table_name: Optional[str] = None):
        self.pat = Config.AIRTABLE_PAT  # Personal Access Token
        self.base_id = Config.AIRTABLE_BASE_ID
        self.table_name = table_name or Config.AIRTABLE_TABLE_NAME
        self.tables = Config.AIRTABLE_TABLES  # List of all tables
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}"
        self.headers = {
            'Authorization': f'Bearer {self.pat}',
            'Content-Type': 'application/json'
        }
    
    def create_headers(self) -> Dict[str, str]:
        """Create headers for Airtable API requests"""
        return {
            'Authorization': f'Bearer {self.pat}',
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
    
    def get_table_names(self) -> List[str]:
        """Get list of available table names"""
        return [table.strip() for table in self.tables]
    
    def test_all_tables(self) -> Dict[str, bool]:
        """Test connection to all configured tables"""
        results = {}
        for table in self.get_table_names():
            try:
                response = requests.get(
                    f"{self.base_url}/{table}?maxRecords=1",
                    headers=self.headers
                )
                results[table] = response.status_code == 200
                if results[table]:
                    print(f"✅ Table '{table}' connection successful")
                else:
                    print(f"❌ Table '{table}' connection failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Table '{table}' connection error: {e}")
                results[table] = False
        return results

    def test_connection(self) -> bool:
        """Test the connection to Airtable (tests all configured tables)"""
        print(f"🔍 Testing connection to {len(self.get_table_names())} tables...")
        results = self.test_all_tables()
        all_successful = all(results.values())
        
        if all_successful:
            print("✅ All Airtable tables accessible")
        else:
            failed_tables = [table for table, success in results.items() if not success]
            print(f"❌ Failed to connect to tables: {', '.join(failed_tables)}")
        
        return all_successful
    
    def push_contacts(self, contacts: List[Dict[str, Any]], clear_existing: bool = False) -> bool:
        """
        Push contacts to Airtable Contacts table
        """
        try:
            print(f"Pushing {len(contacts)} contacts to Airtable...")
            
            # Prepare contact data for Airtable
            contact_records = []
            for contact in contacts:
                record_data = {
                    "fields": {
                        "Full Name": f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
                        "Email": contact.get('email', ''),
                        "Title / Role": contact.get('title', ''),
                        "LinkedIn Profile": contact.get('linkedin_url', ''),
                        "Company": contact.get('company_name', ''),
                        "Status": "New"
                    }
                }
                contact_records.append(record_data)
            
            # Write to Contacts table
            return self.write_records_to_table("Contacts", contact_records)
            
        except Exception as e:
            print(f"❌ Failed to push contacts: {e}")
            return False
    
    def write_records_to_table(self, table_name: str, records: List[Dict[str, Any]]) -> bool:
        """
        Write records to a specific Airtable table
        """
        try:
            url = f"{self.base_url}/{table_name}"
            
            # Airtable allows up to 10 records per request
            batch_size = 10
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                
                response = requests.post(
                    url,
                    headers=self.headers,
                    json={"records": batch}
                )
                
                if response.status_code != 200:
                    print(f"❌ Failed to write batch to {table_name}: {response.status_code}")
                    return False
                
                print(f"✅ Wrote batch {i//batch_size + 1} to {table_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error writing to {table_name}: {e}")
            return False
    
    def get_contacts_for_email_generation(self) -> List[Dict[str, Any]]:
        """
        Get contacts from Airtable that need email generation
        """
        try:
            url = f"{self.base_url}/Contacts"
            params = {
                'filterByFormula': '{Status} = "New"'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                contacts = []
                for record in data.get('records', []):
                    contact = {
                        'id': record['id'],
                        'full_name': record['fields'].get('Full Name', ''),
                        'email': record['fields'].get('Email', ''),
                        'title': record['fields'].get('Title / Role', ''),
                        'company': record['fields'].get('Company', ''),
                        'linkedin_url': record['fields'].get('LinkedIn Profile', '')
                    }
                    contacts.append(contact)
                
                print(f"✅ Retrieved {len(contacts)} contacts from Airtable for email generation")
                return contacts
            else:
                print(f"❌ Failed to get contacts: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting contacts: {e}")
            return []
    
    def store_generated_emails(self, emails: List[Dict[str, Any]]) -> bool:
        """
        Store generated emails in Airtable Emails table
        """
        try:
            print(f"Storing {len(emails)} generated emails in Airtable...")
            
            email_records = []
            for email in emails:
                record_data = {
                    "fields": {
                        "To": email.get('to', ''),
                        "Subject": email.get('subject', ''),
                        "Body": email.get('body', ''),
                        "Send Now": False,  # Manual control - user must check this to send
                        "Send Result": "Pending"
                    }
                }
                email_records.append(record_data)
            
            return self.write_records_to_table("Emails", email_records)
            
        except Exception as e:
            print(f"❌ Failed to store emails: {e}")
            return False
    
    def get_emails_to_send(self) -> List[Dict[str, Any]]:
        """
        Get emails from Airtable that are ready to send
        """
        try:
            url = f"{self.base_url}/Emails"
            params = {
                'filterByFormula': 'AND({Send Now} = TRUE(), {Send Result} = "Pending")'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                emails = []
                for record in data.get('records', []):
                    email = {
                        'id': record['id'],
                        'to': record['fields'].get('To', ''),
                        'subject': record['fields'].get('Subject', ''),
                        'body': record['fields'].get('Body', '')
                    }
                    emails.append(email)
                
                print(f"✅ Retrieved {len(emails)} emails ready to send from Airtable")
                return emails
            else:
                print(f"❌ Failed to get emails: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting emails: {e}")
            return []
    
    def update_email_status(self, email_id: str, success: bool) -> bool:
        """
        Update email status in Airtable after sending
        """
        try:
            url = f"{self.base_url}/Emails/{email_id}"
            
            update_data = {
                "fields": {
                    "Send Now": False,
                    "Send Result": "Sent" if success else "Failed",
                    "Sent At": time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                }
            }
            
            if not success:
                update_data["fields"]["Error"] = "Failed to send email"
            
            response = requests.patch(url, headers=self.headers, json=update_data)
            
            if response.status_code == 200:
                print(f"✅ Updated email status for {email_id}")
                return True
            else:
                print(f"❌ Failed to update email status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating email status: {e}")
            return False
