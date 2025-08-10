"""
BDR AI - Business Development Representative Automation Tool

A comprehensive B2B lead generation and outreach automation system that integrates
Apollo API, Airtable, OpenAI, and Gmail to create personalized outreach campaigns.

This package provides:
- Lead generation from Apollo API
- Data storage and management in Airtable
- AI-powered personalized email generation
- Automated email sending via Gmail API
- Lead scoring and qualification
- Caching and rate limiting
- AWS Lambda deployment support
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .config import Config
from .apollo_api import ApolloAPI
from .airtable_api import AirtableAPI
from .email_sender import GmailSender
from .outreach import OutreachGenerator
from .process_leads import LeadProcessor

__all__ = [
    "Config",
    "ApolloAPI", 
    "AirtableAPI",
    "GmailSender",
    "OutreachGenerator",
    "LeadProcessor",
]
