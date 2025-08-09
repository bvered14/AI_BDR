import json
import boto3
import os
from typing import Dict, Any, List

# Import your existing Airtable logic
import sys
sys.path.append('/opt/python/lib/python3.9/site-packages')
from airtable_api import AirtableAPI
from config import Config

def lambda_handler(event, context):
    """
    Lambda function to store leads in Airtable
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
        
        # Initialize Airtable API
        airtable_api = AirtableAPI()
        
        # Store leads in Airtable
        success = airtable_api.push_leads(processed_leads, clear_existing=False)
        
        if success:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'stored_count': len(processed_leads),
                    'message': f'Successfully stored {len(processed_leads)} leads in Airtable'
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Failed to store leads in Airtable',
                    'message': 'Airtable storage failed'
                })
            }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to store leads'
            })
        }
