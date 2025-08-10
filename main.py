#!/usr/bin/env python3
"""
BDR AI - Main Entry Point
=========================

Command-line interface for the BDR automation pipeline.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from bdr_ai.config import Config
    from bdr_ai.apollo_api import ApolloAPI
    from bdr_ai.airtable_api import AirtableAPI
    from bdr_ai.outreach import OutreachGenerator
    from bdr_ai.process_leads import LeadProcessor
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


def run_pipeline(max_leads=5, min_score=0.6, preview_only=False, no_email=False, 
                force_refresh=False, demo=False):
    """
    Run the complete BDR automation pipeline.
    
    Args:
        max_leads (int): Maximum number of leads to process
        min_score (float): Minimum score threshold for leads
        preview_only (bool): Only preview emails without sending
        no_email (bool): Skip email sending entirely
        force_refresh (bool): Force refresh Apollo cache
        demo (bool): Run in demo mode with sample data
    """
    print("=" * 60)
    print("BDR AI - LEAD GENERATION PIPELINE")
    print("=" * 60)
    
    try:
        # 1. Validate configuration
        print("\n1. Validating configuration...")
        Config.validate_required()
        print("✓ Configuration validated")
        
        if demo:
            print("\n🎭 Running in DEMO mode with sample data...")
            # Demo mode implementation would go here
            return
        
        # 2. Initialize components
        print("\n2. Initializing components...")
        apollo = ApolloAPI()
        airtable = AirtableAPI()
        processor = LeadProcessor()
        email_gen = OutreachGenerator()
        gmail = GmailSender()
        print("✓ Components initialized")
        
        # 3. Fetch leads from Apollo
        print(f"\n3. Fetching up to {max_leads} leads from Apollo API...")
        leads = apollo.fetch_leads(max_leads=max_leads, force_refresh=force_refresh)
        if not leads:
            print("❌ No leads fetched from Apollo API")
            return
        print(f"✓ Fetched {len(leads)} leads from Apollo API")
        
        # 4. Process and rank leads
        print(f"\n4. Processing and ranking leads (min score: {min_score})...")
        ranked_leads = processor.process_leads(leads, min_score=min_score)
        if not ranked_leads:
            print("❌ No leads met the minimum score threshold")
            return
        print(f"✓ Processed and ranked {len(ranked_leads)} leads")
        
        # 5. Store leads in Airtable
        print("\n5. Storing leads in Airtable...")
        airtable.push_leads(ranked_leads)
        print("✓ Successfully stored leads in Airtable")
        
        # 6. Generate personalized emails
        print("\n6. Generating personalized outreach emails...")
        emails = email_gen.generate_emails_for_leads(ranked_leads)
        print(f"✓ Generated {len(emails)} personalized emails")
        
        # 7. Send emails (if not preview mode)
        if not preview_only and not no_email:
            print(f"\n7. Sending {len(emails)} emails via Gmail...")
            gmail.send_emails_to_leads(emails)
            print("✓ Emails sent successfully")
        elif preview_only:
            print("\n7. Preview mode - emails not sent")
            for i, email in enumerate(emails[:3], 1):  # Show first 3
                print(f"\n--- Email {i} ---")
                print(f"To: {email.get('to', 'N/A')}")
                print(f"Subject: {email.get('subject', 'N/A')}")
                print(f"Body: {email.get('body', 'N/A')[:200]}...")
        
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        print(f"\n❌ Pipeline failed: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="BDR AI - Business Development Representative Automation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with default settings (5 leads)
  python main.py --max-leads 10     # Process 10 leads
  python main.py --preview-only     # Preview emails without sending
  python main.py --demo             # Run in demo mode
  python main.py --min-score 0.8    # Only process high-quality leads
        """
    )
    
    parser.add_argument(
        "--max-leads", 
        type=int, 
        default=Config.MAX_LEADS_TO_PROCESS,
        help=f"Maximum number of leads to process (default: {Config.MAX_LEADS_TO_PROCESS})"
    )
    
    parser.add_argument(
        "--min-score", 
        type=float, 
        default=0.6,
        help="Minimum score threshold for leads (default: 0.6)"
    )
    
    parser.add_argument(
        "--preview-only", 
        action="store_true",
        help="Only preview emails without sending"
    )
    
    parser.add_argument(
        "--no-email", 
        action="store_true",
        help="Skip email sending entirely"
    )
    
    parser.add_argument(
        "--force-refresh", 
        action="store_true",
        help="Force refresh Apollo cache"
    )
    
    parser.add_argument(
        "--demo", 
        action="store_true",
        help="Run in demo mode with sample data"
    )
    
    parser.add_argument(
        "--cache-status", 
        action="store_true",
        help="Show Apollo cache status"
    )
    
    parser.add_argument(
        "--clear-cache", 
        action="store_true",
        help="Clear Apollo cache"
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
    
    # Handle cache operations
    if args.cache_status:
        apollo = ApolloAPI()
        apollo.print_cache_status()
        return
    
    if args.clear_cache:
        apollo = ApolloAPI()
        apollo.clear_cache()
        print("✓ Cache cleared successfully")
        return
    
    # Run the pipeline
    run_pipeline(
        max_leads=args.max_leads,
        min_score=args.min_score,
        preview_only=args.preview_only,
        no_email=args.no_email,
        force_refresh=args.force_refresh,
        demo=args.demo
    )


if __name__ == "__main__":
    main()
