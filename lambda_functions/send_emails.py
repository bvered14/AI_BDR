import json
import boto3
import os
from typing import Dict, Any, List

# Import your existing email sender logic
import sys
sys.path.append('/opt/python/lib/python3.9/site-packages')
from email_sender import GmailSender
from config import Config

def lambda_handler(event, context):
    """
    Lambda function to send emails via Gmail
    """
    try:
        # Validate required environment variables FIRST
        Config.validate_required()
        
        # Get emails from previous step
        emails = event.get('emails', [])
        
        if not emails:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No emails provided',
                    'message': 'Email data is required'
                })
            }
        
        # Initialize Gmail sender
        email_sender = GmailSender()
        
        # Send emails
        email_results = email_sender.send_emails_to_leads(emails)
        
        # Calculate success metrics
        successful_sends = sum(1 for r in email_results if r['success'])
        failed_sends = len(email_results) - successful_sends
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'total_emails': len(emails),
                'successful_sends': successful_sends,
                'failed_sends': failed_sends,
                'success_rate': round((successful_sends / len(emails)) * 100, 2),
                'message': f'Successfully sent {successful_sends}/{len(emails)} emails'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to send emails'
            })
        }
