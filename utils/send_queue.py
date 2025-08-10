#!/usr/bin/env python3
"""
BDR AI - Email Queue Sender
===========================

Utility script to send emails from Airtable based on "Send Now" flag.
This script can be run independently to process queued emails.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from bdr_ai.config import Config
    from bdr_ai.airtable_api import AirtableAPI
    from bdr_ai.email_sender import GmailSender
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def send_queued_emails(dry_run=False, max_emails=None):
    """
    Send emails from Airtable that have "Send Now" flag set to True.
    
    Args:
        dry_run (bool): If True, only preview emails without sending
        max_emails (int): Maximum number of emails to send
    """
    print("📧 BDR AI - Email Queue Sender")
    print("=" * 50)
    
    try:
        # Initialize components
        airtable = AirtableAPI("Emails")
        gmail = GmailSender()
        
        # Get emails with "Send Now" flag
        print("\n1. Fetching queued emails from Airtable...")
        emails_to_send = airtable.get_emails_to_send()
        
        if not emails_to_send:
            print("✅ No emails queued for sending")
            return
        
        print(f"📬 Found {len(emails_to_send)} emails to send")
        
        # Limit emails if specified
        if max_emails and len(emails_to_send) > max_emails:
            emails_to_send = emails_to_send[:max_emails]
            print(f"📝 Limiting to {max_emails} emails")
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - Previewing emails:")
            for i, email in enumerate(emails_to_send, 1):
                print(f"\n--- Email {i} ---")
                print(f"To: {email.get('To', 'N/A')}")
                print(f"Subject: {email.get('Subject', 'N/A')}")
                print(f"Body: {email.get('Body', 'N/A')[:200]}...")
            print(f"\n✅ Dry run completed - {len(emails_to_send)} emails would be sent")
            return
        
        # Send emails
        print(f"\n2. Sending {len(emails_to_send)} emails...")
        successful_sends = 0
        failed_sends = 0
        
        for i, email in enumerate(emails_to_send, 1):
            try:
                print(f"📤 Sending email {i}/{len(emails_to_send)} to {email.get('To', 'N/A')}")
                
                # Send email
                success = gmail.send_email(
                    to_email=email.get('To'),
                    subject=email.get('Subject'),
                    body=email.get('Body')
                )
                
                if success:
                    # Update Airtable record
                    airtable.update_email_status(
                        email['id'],
                        sent=True,
                        error_message=None
                    )
                    successful_sends += 1
                    print(f"✅ Email sent successfully")
                else:
                    airtable.update_email_status(
                        email['id'],
                        sent=False,
                        error_message="Failed to send email"
                    )
                    failed_sends += 1
                    print(f"❌ Failed to send email")
                    
            except Exception as e:
                logger.error(f"Error sending email {i}: {e}")
                airtable.update_email_status(
                    email['id'],
                    sent=False,
                    error_message=str(e)
                )
                failed_sends += 1
                print(f"❌ Error: {e}")
        
        # Summary
        print(f"\n" + "=" * 50)
        print("📊 EMAIL SENDING SUMMARY")
        print("=" * 50)
        print(f"Total emails processed: {len(emails_to_send)}")
        print(f"Successful sends: {successful_sends}")
        print(f"Failed sends: {failed_sends}")
        print(f"Success rate: {(successful_sends/len(emails_to_send)*100):.1f}%")
        
        if successful_sends > 0:
            print(f"\n✅ Successfully sent {successful_sends} emails!")
        if failed_sends > 0:
            print(f"⚠️ {failed_sends} emails failed to send")
            
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        print(f"\n❌ Email sending failed: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="BDR AI - Send queued emails from Airtable",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python utils/send_queue.py              # Send all queued emails
  python utils/send_queue.py --dry-run    # Preview emails without sending
  python utils/send_queue.py --max 5      # Send maximum 5 emails
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview emails without sending"
    )
    
    parser.add_argument(
        "--max",
        type=int,
        help="Maximum number of emails to send"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Send emails
    send_queued_emails(
        dry_run=args.dry_run,
        max_emails=args.max
    )


if __name__ == "__main__":
    main()
