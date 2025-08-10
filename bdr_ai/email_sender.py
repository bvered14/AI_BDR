import os
import time
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
from .config import Config

class GmailSender:
    def __init__(self):
        self.credentials_file = Config.GMAIL_CREDENTIALS_FILE
        self.token_file = Config.GMAIL_TOKEN_FILE
        self.scopes = ['https://www.googleapis.com/auth/gmail.send']
        self.service = None
        self.sender_email = Config.SENDER_EMAIL
    
    def authenticate(self):
        """
        Authenticate with Gmail API
        """
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Gmail credentials file '{self.credentials_file}' not found. "
                        "Please download it from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("Successfully authenticated with Gmail API")
    
    def create_message(self, to_email: str, subject: str, body: str) -> Dict[str, str]:
        """
        Create a Gmail message
        """
        message = MIMEMultipart()
        message['to'] = to_email
        message['from'] = self.sender_email
        message['subject'] = subject
        
        # Add body
        text_part = MIMEText(body, 'plain')
        message.attach(text_part)
        
        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        return {'raw': raw_message}
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send a single email
        """
        try:
            if not self.service:
                self.authenticate()
            
            message = self.create_message(to_email, subject, body)
            
            sent_message = self.service.users().messages().send(
                userId='me', body=message
            ).execute()
            
            print(f"Email sent successfully to {to_email}")
            print(f"Message ID: {sent_message['id']}")
            
            return True
            
        except HttpError as error:
            print(f"Error sending email to {to_email}: {error}")
            return False
    
    def send_email_to_lead(self, email_data: Dict[str, Any]) -> bool:
        """
        Send email to a specific lead
        """
        lead = email_data.get('lead', {})
        to_email = lead.get('email', '')
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        
        if not to_email:
            print("No email address found for lead")
            return False
        
        return self.send_email(to_email, subject, body)
    
    def send_emails_to_leads(self, emails: List[Dict[str, Any]], 
                           delay_seconds: int = 2) -> List[Dict[str, Any]]:
        """
        Send emails to multiple leads with delay between sends
        """
        import time
        
        print(f"Sending {len(emails)} emails...")
        
        results = []
        successful_sends = 0
        
        for i, email_data in enumerate(emails, 1):
            lead = email_data.get('lead', {})
            lead_name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}"
            
            print(f"Sending email {i}/{len(emails)} to {lead_name} ({lead.get('email', '')})")
            
            success = self.send_email_to_lead(email_data)
            
            result = {
                'lead': lead,
                'email_data': email_data,
                'success': success,
                'timestamp': time.time()
            }
            results.append(result)
            
            if success:
                successful_sends += 1
            
            # Add delay between sends to avoid rate limiting
            if i < len(emails):
                print(f"Waiting {delay_seconds} seconds before next email...")
                time.sleep(delay_seconds)
        
        print(f"Email sending complete: {successful_sends}/{len(emails)} successful")
        return results
    
    def send_emails_from_airtable(self, delay_seconds: int = 2) -> List[Dict[str, Any]]:
        """
        Send emails from Airtable Emails table
        """
        from .airtable_api import AirtableAPI
        
        try:
            # Get emails from Airtable that are ready to send
            airtable = AirtableAPI()
            emails = airtable.get_emails_to_send()
            
            if not emails:
                print("No emails found in Airtable ready to send")
                return []
            
            print(f"Found {len(emails)} emails ready to send from Airtable")
            
            # Send emails
            results = []
            for i, email_data in enumerate(emails):
                try:
                    to_email = email_data.get('to', '')
                    subject = email_data.get('subject', '')
                    body = email_data.get('body', '')
                    email_id = email_data.get('id', '')
                    
                    if not to_email:
                        print(f"❌ No email address found for email {i+1}")
                        continue
                    
                    success = self.send_email(to_email, subject, body)
                    
                    # Update Airtable with send result
                    airtable.update_email_status(email_id, success)
                    
                    results.append({
                        'email': to_email,
                        'success': success,
                        'error': None if success else 'Failed to send'
                    })
                    
                    # Rate limiting
                    if i < len(emails) - 1:
                        time.sleep(delay_seconds)
                    
                except Exception as e:
                    print(f"❌ Error sending email {i+1}: {e}")
                    results.append({
                        'email': email_data.get('to', 'unknown'),
                        'success': False,
                        'error': str(e)
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Error sending emails from Airtable: {e}")
            return []
    
    def preview_email(self, email_data: Dict[str, Any]) -> None:
        """
        Preview an email without sending it
        """
        lead = email_data.get('lead', {})
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        
        print("\n" + "="*50)
        print("EMAIL PREVIEW (NOT SENT)")
        print("="*50)
        print(f"From: {self.sender_email}")
        print(f"To: {lead.get('first_name', '')} {lead.get('last_name', '')} <{lead.get('email', '')}>")
        print(f"Subject: {subject}")
        print("-"*50)
        print(body)
        print("="*50)
    
    def get_sending_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary of email sending results
        """
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        summary = {
            'total_emails': len(results),
            'successful_sends': len(successful),
            'failed_sends': len(failed),
            'success_rate': round(len(successful) / len(results) * 100, 2) if results else 0,
            'failed_emails': [r['lead'].get('email', '') for r in failed]
        }
        
        return summary
