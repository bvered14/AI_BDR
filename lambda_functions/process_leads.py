import json
import boto3
import os
from typing import Dict, Any, List

# Import your existing lead processing logic
import sys
sys.path.append('/opt/python/lib/python3.9/site-packages')
from process_leads import LeadProcessor

def lambda_handler(event, context):
    """
    Lambda function to process and rank leads
    """
    try:
        # Get leads from previous step
        leads = event.get('leads', [])
        min_score = float(os.environ.get('MIN_SCORE', 0.6))
        
        if not leads:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No leads provided',
                    'message': 'Leads data is required'
                })
            }
        
        # Initialize lead processor
        processor = LeadProcessor()
        
        # Process and rank leads
        processed_leads = processor.process_leads(leads, min_score)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'processed_leads': processed_leads,
                'count': len(processed_leads),
                'message': f'Successfully processed {len(processed_leads)} leads'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to process leads'
            })
        }
