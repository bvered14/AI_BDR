import json
import boto3
import os
from typing import Dict, Any, List

def lambda_handler(event, context):
    """
    Main orchestrator Lambda function to run the complete pipeline
    """
    try:
        # Get configuration from event or environment
        max_leads = event.get('max_leads', int(os.environ.get('MAX_LEADS', 10)))
        min_score = event.get('min_score', float(os.environ.get('MIN_SCORE', 0.6)))
        
        # Initialize AWS Lambda client
        lambda_client = boto3.client('lambda')
        
        # Step 1: Fetch leads
        print("Step 1: Fetching leads...")
        fetch_response = lambda_client.invoke(
            FunctionName=f"{os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'bdr-lead-pipeline')}-fetch-leads",
            InvocationType='RequestResponse',
            Payload=json.dumps({'max_leads': max_leads})
        )
        
        fetch_result = json.loads(fetch_response['Payload'].read())
        if fetch_result['statusCode'] != 200:
            raise Exception(f"Failed to fetch leads: {fetch_result['body']}")
        
        leads_data = json.loads(fetch_result['body'])
        leads = leads_data['leads']
        
        # Step 2: Process leads
        print("Step 2: Processing leads...")
        process_response = lambda_client.invoke(
            FunctionName=f"{os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'bdr-lead-pipeline')}-process-leads",
            InvocationType='RequestResponse',
            Payload=json.dumps({'leads': leads, 'min_score': min_score})
        )
        
        process_result = json.loads(process_response['Payload'].read())
        if process_result['statusCode'] != 200:
            raise Exception(f"Failed to process leads: {process_result['body']}")
        
        processed_data = json.loads(process_result['body'])
        processed_leads = processed_data['processed_leads']
        
        # Step 3: Store leads
        print("Step 3: Storing leads...")
        store_response = lambda_client.invoke(
            FunctionName=f"{os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'bdr-lead-pipeline')}-store-leads",
            InvocationType='RequestResponse',
            Payload=json.dumps({'processed_leads': processed_leads})
        )
        
        store_result = json.loads(store_response['Payload'].read())
        if store_result['statusCode'] != 200:
            raise Exception(f"Failed to store leads: {store_result['body']}")
        
        # Step 4: Generate emails
        print("Step 4: Generating emails...")
        generate_response = lambda_client.invoke(
            FunctionName=f"{os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'bdr-lead-pipeline')}-generate-emails",
            InvocationType='RequestResponse',
            Payload=json.dumps({'processed_leads': processed_leads})
        )
        
        generate_result = json.loads(generate_response['Payload'].read())
        if generate_result['statusCode'] != 200:
            raise Exception(f"Failed to generate emails: {generate_result['body']}")
        
        emails_data = json.loads(generate_result['body'])
        emails = emails_data['emails']
        
        # Step 5: Send emails
        print("Step 5: Sending emails...")
        send_response = lambda_client.invoke(
            FunctionName=f"{os.environ.get('AWS_LAMBDA_FUNCTION_NAME', 'bdr-lead-pipeline')}-send-emails",
            InvocationType='RequestResponse',
            Payload=json.dumps({'emails': emails})
        )
        
        send_result = json.loads(send_response['Payload'].read())
        if send_result['statusCode'] != 200:
            raise Exception(f"Failed to send emails: {send_result['body']}")
        
        send_data = json.loads(send_result['body'])
        
        # Compile final results
        results = {
            'leads_fetched': len(leads),
            'leads_processed': len(processed_leads),
            'emails_generated': len(emails),
            'emails_sent': send_data['successful_sends'],
            'success_rate': send_data['success_rate'],
            'status': 'completed'
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Pipeline completed successfully',
                'results': results
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Pipeline failed'
            })
        }
