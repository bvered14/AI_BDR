import json
import boto3
import os
from typing import Dict, Any, List

# Import your existing Apollo API logic
import sys
sys.path.append('/opt/python/lib/python3.9/site-packages')
from apollo_api import ApolloAPI

def lambda_handler(event, context):
    """
    Lambda function to fetch leads from Apollo API
    """
    try:
        # Get configuration from environment variables
        max_leads = int(os.environ.get('MAX_LEADS', 10))
        
        # Initialize Apollo API
        apollo_api = ApolloAPI()
        
        # Fetch leads
        leads = apollo_api.fetch_leads(max_leads)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'leads': leads,
                'count': len(leads),
                'message': f'Successfully fetched {len(leads)} leads'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to fetch leads'
            })
        }
