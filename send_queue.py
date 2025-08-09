#!/usr/bin/env python3
"""
Send Queue Script for Local Testing
===================================
This script sends emails from the queue for local testing.
It's designed to work with the main pipeline and can be run independently.
"""
import sys
import os
from typing import List, Dict, Any

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from email_sender import GmailSender
    from config import Config
    from airtable_api import AirtableAPI
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

def get_pending_emails() -> List[Dict[str, Any]]:
    """Get emails that are marked as 'Send Now' in Airtable"""
    try:
        airtable = AirtableAPI()
        # Get records where 'Send Now' is checked
        records = airtable.get_records(
            filter_by_formula="{Send Now} = 1"
        )
        
        if not records:
            print("ℹ️  No emails marked for sending in Airtable")
            return []
        
        print(f"📧 Found {len(records)} emails marked for sending")
        return records
        
    except Exception as e:
        print(f"❌ Error fetching pending emails: {e}")
        return []

def send_emails(emails: List[Dict[str, Any]], dry_run: bool = False) -> Dict[str, Any]:
    """Send the pending emails"""
    if not emails:
        return {"sent": 0, "failed": 0, "errors": []}
    
    results = {
        "sent": 0,
        "failed": 0,
        "errors": []
    }
    
    try:
        gmail_sender = GmailSender()
        
        for i, email_record in enumerate(emails, 1):
            try:
                # Extract email data
                email_data = email_record.get('fields', {})
                to_email = email_data.get('Email')
                subject = email_data.get('Subject', Config.EMAIL_SUBJECT)
                body = email_data.get('Email Body')
                
                if not to_email:
                    error_msg = f"Record {i}: Missing email address"
                    results["errors"].append(error_msg)
                    results["failed"] += 1
                    continue
                
                if not body:
                    error_msg = f"Record {i}: Missing email body"
                    results["errors"].append(error_msg)
                    results["failed"] += 1
                    continue
                
                print(f"📤 Sending email {i}/{len(emails)} to {to_email}")
                
                if not dry_run:
                    # Actually send the email
                    gmail_sender.send_email(to_email, subject, body)
                    
                    # Update Airtable to mark as sent
                    airtable = AirtableAPI()
                    airtable.update_record(
                        email_record['id'],
                        {
                            'Send Now': False,
                            'Sent': True,
                            'Sent Date': airtable.get_current_timestamp()
                        }
                    )
                    
                    results["sent"] += 1
                    print(f"✅ Email sent successfully to {to_email}")
                else:
                    print(f"🔍 [DRY RUN] Would send email to {to_email}")
                    print(f"   Subject: {subject}")
                    print(f"   Body preview: {body[:100]}...")
                    results["sent"] += 1
                    
            except Exception as e:
                error_msg = f"Record {i}: {str(e)}"
                results["errors"].append(error_msg)
                results["failed"] += 1
                print(f"❌ Failed to send email {i}: {e}")
                
    except Exception as e:
        print(f"❌ Error initializing email sender: {e}")
        results["errors"].append(f"Initialization error: {e}")
    
    return results

def main():
    """Main function for the send queue script"""
    print("🚀 Send Queue Script for Local Testing")
    print("=" * 50)
    
    # Check if we want to do a dry run
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    
    if dry_run:
        print("🔍 Running in DRY RUN mode - no emails will actually be sent")
    
    # Validate configuration
    try:
        Config.validate_required()
        print("✓ Configuration validated")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Get pending emails
    print("\n1. Fetching pending emails from Airtable...")
    pending_emails = get_pending_emails()
    
    if not pending_emails:
        print("No emails to send. Make sure to:")
        print("1. Run the main pipeline first")
        print("2. Mark some rows as 'Send Now' in Airtable")
        return
    
    # Send emails
    print(f"\n2. Sending {len(pending_emails)} emails...")
    results = send_emails(pending_emails, dry_run=dry_run)
    
    # Show results
    print(f"\n📊 Results:")
    print(f"   ✅ Sent: {results['sent']}")
    print(f"   ❌ Failed: {results['failed']}")
    
    if results['errors']:
        print(f"\n❌ Errors:")
        for error in results['errors']:
            print(f"   • {error}")
    
    if dry_run:
        print(f"\n🔍 This was a dry run. To actually send emails, run:")
        print(f"   python send_queue.py")
    else:
        print(f"\n🎉 Email sending completed!")

if __name__ == "__main__":
    main()
