#!/usr/bin/env python3
"""
GTM Lead Generation Pipeline
============================

This script orchestrates the complete lead generation pipeline:
1. Fetch B2B leads from Apollo API
2. Process and rank leads
3. Push to Airtable
4. Generate personalized emails
5. Send emails via Gmail

Usage:
    python main.py [--max-leads N] [--min-score S] [--preview-only] [--no-email]
"""

import argparse
import sys
import time
from typing import List, Dict, Any

from config import Config
from apollo_api import ApolloAPI
from process_leads import LeadProcessor
from airtable_api import AirtableAPI
from outreach import OutreachGenerator
from email_sender import GmailSender

class GTMLeadPipeline:
    def __init__(self):
        # Validate required environment variables FIRST
        Config.validate_required()
        
        self.apollo_api = ApolloAPI()
        self.lead_processor = LeadProcessor()
        self.airtable_api = AirtableAPI()
        self.outreach_generator = OutreachGenerator()
        self.email_sender = GmailSender()
    
    def run_pipeline(self, max_leads: int = 5, min_score: float = 0.6, 
                    preview_only: bool = None, no_email: bool = False, 
                    force_refresh: bool = False) -> Dict[str, Any]:
        """
        Run the complete GTM lead generation pipeline
        
        Args:
            max_leads: Maximum number of leads to fetch
            min_score: Minimum score threshold for leads
            preview_only: Override Config.PREVIEW_ONLY setting
            no_email: Skip email sending entirely
            force_refresh: Force refresh from Apollo API (ignore cache)
        """
        start_time = time.time()
        
        # Use Config.PREVIEW_ONLY if preview_only is None
        if preview_only is None:
            preview_only = Config.PREVIEW_ONLY
        
        results = {
            'leads_fetched': 0,
            'leads_processed': 0,
            'emails_generated': 0,
            'emails_sent': 0,
            'success': False,
            'errors': []
        }
        
        try:
            # Step 1: Validate configuration
            print("\n1. Validating configuration...")
            Config.validate_required()
            print("✓ Configuration validated")
            
            # Step 1.5: Show cache status
            print("\n1.5. Checking Apollo API cache...")
            self.apollo_api.print_cache_status()
            
            # Step 2: Fetch leads from Apollo
            print(f"\n2. Fetching up to {max_leads} leads from Apollo API...")
            leads = self.apollo_api.fetch_leads(max_leads, force_refresh=force_refresh)
            results['leads_fetched'] = len(leads)
            
            if not leads:
                print("❌ No leads fetched from Apollo API")
                return results
            
            print(f"✓ Fetched {len(leads)} leads from Apollo API")
            
            # Step 3: Process and rank leads
            print(f"\n3. Processing and ranking leads (min score: {min_score})...")
            processed_leads = self.lead_processor.process_leads(leads, min_score)
            results['leads_processed'] = len(processed_leads)
            
            if not processed_leads:
                print("❌ No leads met the minimum score threshold")
                return results
            
            print(f"✓ Processed and ranked {len(processed_leads)} leads")
            
            # Step 4: Push to Airtable
            print("\n4. Pushing leads to Airtable...")
            airtable_success = self.airtable_api.push_leads(processed_leads)
            
            if airtable_success:
                print("✓ Successfully pushed leads to Airtable")
            else:
                print("⚠ Warning: Failed to push leads to Airtable")
                results['errors'].append("Airtable push failed")
            
            # Step 5: Generate personalized emails
            print("\n5. Generating personalized outreach emails...")
            emails = self.outreach_generator.generate_emails_for_leads(processed_leads)
            results['emails_generated'] = len(emails)
            
            print(f"✓ Generated {len(emails)} personalized emails")
            
            # Step 6: Handle email sending based on preview mode
            if preview_only:
                print(f"\n6. PREVIEW MODE - Emails will be displayed but not sent")
                print(f"   To send emails, set PREVIEW_ONLY=false in your .env file")
                results['emails_sent'] = 0
            elif no_email:
                print("\n6. Skipping email sending (--no-email flag)")
                results['emails_sent'] = 0
            elif emails:
                print(f"\n6. Sending {len(emails)} emails via Gmail...")
                email_results = self.email_sender.send_emails_to_leads(emails)
                
                successful_sends = sum(1 for r in email_results if r['success'])
                results['emails_sent'] = successful_sends
                
                print(f"✓ Sent {successful_sends}/{len(emails)} emails successfully")
                
                # Print email summary
                summary = self.email_sender.get_sending_summary(email_results)
                print(f"\nEmail Sending Summary:")
                print(f"  Total emails: {summary['total_emails']}")
                print(f"  Successful: {summary['successful_sends']}")
                print(f"  Failed: {summary['failed_sends']}")
                print(f"  Success rate: {summary['success_rate']}%")
                
                if summary['failed_emails']:
                    print(f"  Failed emails: {', '.join(summary['failed_emails'])}")
            else:
                print("\n6. No emails to send")
                results['emails_sent'] = 0
            
            # Calculate execution time
            execution_time = time.time() - start_time
            results['execution_time'] = round(execution_time, 2)
            results['success'] = True
            
            print(f"\n" + "="*60)
            print("PIPELINE COMPLETED SUCCESSFULLY")
            print("="*60)
            print(f"Execution time: {execution_time:.2f} seconds")
            print(f"Leads fetched: {results['leads_fetched']}")
            print(f"Leads processed: {results['leads_processed']}")
            print(f"Emails generated: {results['emails_generated']}")
            print(f"Emails sent: {results['emails_sent']}")
            
            if preview_only:
                print(f"Mode: PREVIEW (emails displayed but not sent)")
            
            return results
            
        except Exception as e:
            execution_time = time.time() - start_time
            results['execution_time'] = round(execution_time, 2)
            results['errors'].append(str(e))
            print(f"\n❌ Pipeline failed: {e}")
            return results
    
    def run_demo(self):
        """
        Run a demo with sample data (no API calls)
        """
        print("="*60)
        print("DEMO MODE - Using Sample Data")
        print("="*60)
        
        # Sample leads for demo
        sample_leads = [
            {
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john.smith@techcorp.com',
                'title': 'CTO',
                'company_name': 'TechCorp Solutions',
                'company_size': 150,
                'company_industry': 'Software',
                'company_location': 'San Francisco, CA',
                'region': 'North America',
                'linkedin_url': 'https://linkedin.com/in/johnsmith',
                'apollo_id': 'demo_1',
                'company_domain': 'techcorp.com',
                'company_revenue': '$10M-50M',
                'company_founded': '2015'
            },
            {
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah.johnson@securenet.com',
                'title': 'Head of Security',
                'company_name': 'SecureNet Systems',
                'company_size': 75,
                'company_industry': 'Cybersecurity',
                'company_location': 'London, UK',
                'region': 'Europe',
                'linkedin_url': 'https://linkedin.com/in/sarahjohnson',
                'apollo_id': 'demo_2',
                'company_domain': 'securenet.com',
                'company_revenue': '$5M-10M',
                'company_founded': '2018'
            },
            {
                'first_name': 'Michael',
                'last_name': 'Chen',
                'email': 'michael.chen@fintechpro.com',
                'title': 'VP of Engineering',
                'company_name': 'FinTech Pro',
                'company_size': 200,
                'company_industry': 'Fintech',
                'company_location': 'New York, NY',
                'region': 'North America',
                'linkedin_url': 'https://linkedin.com/in/michaelchen',
                'apollo_id': 'demo_3',
                'company_domain': 'fintechpro.com',
                'company_revenue': '$10M-50M',
                'company_founded': '2016'
            }
        ]
        
        print(f"\n1. Using {len(sample_leads)} sample leads...")
        
        # Process leads
        print("\n2. Processing and ranking sample leads...")
        processed_leads = self.lead_processor.process_leads(sample_leads, 0.5)
        
        # Generate emails
        print("\n3. Generating personalized emails...")
        emails = self.outreach_generator.generate_emails_for_leads(processed_leads)
        
        # Preview emails
        print("\n4. Previewing generated emails...")
        for i, email_data in enumerate(emails, 1):
            print(f"\n--- Email {i} ---")
            self.outreach_generator.preview_email(processed_leads[i-1])
        
        print(f"\n✓ Demo completed successfully!")
        print(f"Processed {len(processed_leads)} leads")
        print(f"Generated {len(emails)} emails")

def main():
    parser = argparse.ArgumentParser(description='GTM Lead Generation Pipeline')
    parser.add_argument('--max-leads', type=int, default=5,
                       help='Maximum number of leads to fetch (default: 5)')
    parser.add_argument('--min-score', type=float, default=0.6,
                       help='Minimum score threshold for leads (default: 0.6)')
    parser.add_argument('--preview-only', action='store_true',
                       help='Only preview emails without sending')
    parser.add_argument('--no-email', action='store_true',
                       help='Skip email sending')
    parser.add_argument('--force-refresh', action='store_true',
                       help='Force refresh from Apollo API (ignore cache)')
    parser.add_argument('--cache-status', action='store_true',
                       help='Show Apollo API cache status')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Clear Apollo API cache')
    parser.add_argument('--demo', action='store_true',
                       help='Run in demo mode with sample data')
    
    args = parser.parse_args()
    
    # Create pipeline instance
    pipeline = GTMLeadPipeline()
    
    try:
        if args.demo:
            pipeline.run_demo()
        elif args.cache_status:
            pipeline.apollo_api.print_cache_status()
        elif args.clear_cache:
            pipeline.apollo_api.clear_cache()
            print("✅ Cache cleared successfully")
        else:
            results = pipeline.run_pipeline(
                max_leads=args.max_leads,
                min_score=args.min_score,
                preview_only=args.preview_only,
                no_email=args.no_email,
                force_refresh=args.force_refresh
            )
            
            if not results['success']:
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
