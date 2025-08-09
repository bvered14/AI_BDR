import json
import boto3
import os
import logging
import tempfile
from typing import Dict, Any, List

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Import your existing email sender logic
import sys
sys.path.append('/opt/python/lib/python3.9/site-packages')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from email_sender import GmailSender
    from config import Config
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    raise

def lambda_handler(event, context):
    """
    Lambda function to send emails via Gmail
    
    Expected event structure:
    {
        "emails": [
            {
                "lead": {"email": "test@example.com", "first_name": "John", "last_name": "Doe"},
                "subject": "Your subject",
                "body": "Your email body"
            }
        ]
    }
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Validate required environment variables FIRST
        Config.validate_required()
        
        # Get emails from previous step
        emails = event.get('emails', [])
        
        if not emails:
            logger.warning("No emails provided in event")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No emails provided',
                    'message': 'Email data is required',
                    'event': event
                })
            }
        
        logger.info(f"Processing {len(emails)} emails")
        
        # Initialize Gmail sender with Lambda-specific config
        try:
            # Override config for Lambda environment
            if not os.path.exists(Config.GMAIL_CREDENTIALS_FILE):
                # Try to get credentials from environment or Secrets Manager
                logger.info("Gmail credentials file not found, checking environment...")
                
                # Check if credentials are in environment variables
                gmail_creds = os.getenv('GMAIL_CREDENTIALS_JSON')
                if gmail_creds:
                    # Write credentials to temp file
                    temp_creds_file = os.path.join(tempfile.gettempdir(), 'gmail_credentials.json')
                    with open(temp_creds_file, 'w') as f:
                        f.write(gmail_creds)
                    os.environ['GMAIL_CREDENTIALS_FILE'] = temp_creds_file
                    logger.info(f"Gmail credentials written to temp file: {temp_creds_file}")
                
                # Check if token is in environment variables
                gmail_token = os.getenv('GMAIL_TOKEN_JSON')
                if gmail_token:
                    temp_token_file = os.path.join(tempfile.gettempdir(), 'gmail_token.json')
                    with open(temp_token_file, 'w') as f:
                        f.write(gmail_token)
                    os.environ['GMAIL_TOKEN_FILE'] = temp_token_file
                    logger.info(f"Gmail token written to temp file: {temp_token_file}")
            
            email_sender = GmailSender()
            logger.info("GmailSender initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GmailSender: {e}")
            raise
        
        # Send emails
        email_results = email_sender.send_emails_to_leads(emails)
        
        # Calculate success metrics
        successful_sends = sum(1 for r in email_results if r.get('success', False))
        failed_sends = len(email_results) - successful_sends
        
        success_rate = round((successful_sends / len(emails)) * 100, 2) if emails else 0
        
        response_data = {
            'total_emails': len(emails),
            'successful_sends': successful_sends,
            'failed_sends': failed_sends,
            'success_rate': success_rate,
            'message': f'Successfully sent {successful_sends}/{len(emails)} emails'
        }
        
        logger.info(f"Email sending complete: {successful_sends}/{len(emails)} successful ({success_rate}%)")
        
        return {
            'statusCode': 200,
            'body': json.dumps(response_data)
        }
        
    except ValueError as e:
        # Configuration validation errors
        logger.error(f"Configuration error: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Configuration error',
                'message': str(e)
            })
        }
    except Exception as e:
        logger.error(f"Unexpected error in lambda_handler: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': f'Failed to send emails: {str(e)}'
            })
        }
