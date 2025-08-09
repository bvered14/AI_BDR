import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Apollo API Configuration
    APOLLO_API_KEY = os.getenv('APOLLO_API_KEY')
    APOLLO_BASE_URL = 'https://api.apollo.io/v1'
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # Cost-optimized default
    
    # Airtable Configuration
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'Leads')
    
    # Gmail Configuration
    GMAIL_CREDENTIALS_FILE = os.getenv('GMAIL_CREDENTIALS_FILE', 'gmail_credentials.json')
    GMAIL_TOKEN_FILE = os.getenv('GMAIL_TOKEN_FILE', 'gmail_token.json')
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    
    # Lead Generation Settings
    JOB_TITLES = ['CTO', 'Head of Security', 'Chief Technology Officer', 'VP of Engineering']
    COMPANY_SIZE_MIN = 50
    COMPANY_SIZE_MAX = 500
    REGIONS = ['North America', 'Europe']
    
    # Scoring Weights (exposed for transparency)
    INDUSTRY_WEIGHT = 0.4
    COMPANY_SIZE_WEIGHT = 0.3
    REGION_WEIGHT = 0.3
    
    # Email Settings
    EMAIL_SUBJECT = "Quick question about your tech stack"
    MAX_LEADS_TO_PROCESS = 10
    
    # Pipeline Settings
    PREVIEW_ONLY = os.getenv('PREVIEW_ONLY', 'true').lower() == 'true'  # Default to preview mode
    
    @classmethod
    def validate_required(cls):
        """Validate that all required environment variables are set - FAIL FAST"""
        required_vars = [
            'APOLLO_API_KEY',
            'OPENAI_API_KEY', 
            'AIRTABLE_API_KEY',
            'AIRTABLE_BASE_ID',
            'SENDER_EMAIL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"❌ Missing required environment variables: {', '.join(missing_vars)}\n"
                           f"Please check your .env file or environment variables.")
        
        print("✅ All required environment variables are set")
        return True

    @classmethod
    def validate_config(cls):
        """Legacy method - use validate_required() instead"""
        return cls.validate_required()
