import json
import boto3
import os
from typing import Dict, Any, List

# Import your existing outreach logic
import sys
sys.path.append('/opt/python/lib/python3.9/site-packages')
from outreach import OutreachGenerator
from config import Config

def lambda_handler(event, context):
    """
    Lambda function to generate personalized emails
    """
    try:
        # Validate required environment variables FIRST
        Config.validate_required()
        
        # Get processed leads from previous step
        processed_leads = event.get('processed_leads', [])
        
        if not processed_leads:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No processed leads provided',
                    'message': 'Processed leads data is required'
                })
            }
        
        # Initialize outreach generator
        outreach_generator = OutreachGenerator()
        
        # Generate emails for leads
        emails = outreach_generator.generate_emails_for_leads(processed_leads)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'emails': emails,
                'count': len(emails),
                'message': f'Successfully generated {len(emails)} personalized emails'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to generate emails'
            })
        }
