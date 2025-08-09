# Local Testing Guide

This guide will help you test the entire B2B lead generation pipeline locally before deploying to AWS Lambda.

## Prerequisites

1. **Environment Variables**: Make sure you have a `.env` file with all required API keys:
   ```bash
   APOLLO_API_KEY=your_apollo_key
   OPENAI_API_KEY=your_openai_key
   AIRTABLE_API_KEY=your_airtable_key
   AIRTABLE_BASE_ID=your_base_id
   AIRTABLE_TABLE_NAME=your_table_name
   GMAIL_CLIENT_ID=your_gmail_client_id
   GMAIL_CLIENT_SECRET=your_gmail_client_secret
   GMAIL_REFRESH_TOKEN=your_gmail_refresh_token
   ```

2. **Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Testing Workflow (Start Small!)

**⚠️ IMPORTANT: Start with just 1-2 contacts to conserve Apollo API credits!**

### Step 1: Test Apollo API (First Run - Will Cache)
```bash
python main.py --max-leads 2 --preview-only
```

**What this does:**
- Fetches only 2 leads from Apollo API (minimal API usage)
- Caches the response locally (saves API credits)
- Shows preview of what would be processed
- **First run**: Makes actual API call and caches results
- **Subsequent runs**: Uses cached data (no API calls)

**Expected output:**
```
🚀 B2B Lead Generation Pipeline
================================
✓ Configuration validated

1.5. Checking Apollo API cache...
📊 Cache Status:
   • Cache enabled: True
   • Cache file: cache/apollo_leads_cache.json
   • Cache exists: False
   • Cache valid: False

2. Fetching up to 2 leads from Apollo API...
🔍 Fetching up to 2 leads from Apollo API...
✅ Successfully fetched 2 leads

3. Processing leads with AI...
...
```

### Step 2: Test AI Enrichment and Email Generation
```bash
python main.py --max-leads 2 --no-email
```

**What this does:**
- Uses cached Apollo data (no API calls)
- Processes 2 leads with OpenAI for scoring and enrichment
- Generates personalized emails
- Updates Airtable with all data
- **Does NOT send emails** (just prepares them)

**Expected output:**
```
🚀 B2B Lead Generation Pipeline
================================
✓ Configuration validated

1.5. Checking Apollo API cache...
📊 Cache Status:
   • Cache enabled: True
   • Cache file: cache/apollo_leads_cache.json
   • Cache exists: True
   • Cache valid: True
   • Cache age: 0.5 hours
   • Using cached data (2 leads)

2. Fetching up to 2 leads from Apollo API...
✅ Using cached data: 2 leads

3. Processing leads with AI...
...
```

### Step 3: Review in Airtable
1. Open your Airtable base
2. Check that 2 new records were added
3. Review the generated emails
4. **Select 1 row** and check the "Send Now" checkbox (start with just 1 email)

### Step 4: Test Email Sending (Dry Run First)
```bash
# Dry run - see what would be sent without actually sending
python send_queue.py --dry-run

# If everything looks good, actually send
python send_queue.py
```

**Expected output (dry run):**
```
🚀 Send Queue Script for Local Testing
==================================================
🔍 Running in DRY RUN mode - no emails will actually be sent
✓ Configuration validated

1. Fetching pending emails from Airtable...
📧 Found 1 email marked for sending

2. Sending 1 email...
🔍 [DRY RUN] Would send email to john@company.com
   Subject: Quick question about your tech stack
   Body preview: Hi John, I noticed your company is using...

📊 Results:
   ✅ Sent: 1
   ❌ Failed: 0

🔍 This was a dry run. To actually send emails, run:
   python send_queue.py
```

## Scaling Up (Only After Everything Works!)

Once you've successfully tested with 1-2 contacts:

1. **Test with 3-5 contacts:**
   ```bash
   python main.py --max-leads 5 --no-email
   ```

2. **Test with 10+ contacts:**
   ```bash
   python main.py --max-leads 10 --no-email
   ```

## Cache Management

### Check Cache Status
```bash
python main.py --cache-status
```

### Clear Cache (if you want fresh data)
```bash
python main.py --clear-cache
```

### Force Refresh (ignore cache)
```bash
python main.py --max-leads 2 --force-refresh
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Make sure you're running from the project root directory
   - Check that all dependencies are installed

2. **API Key Errors**
   - Verify your `.env` file has all required keys
   - Check that the keys are valid and have proper permissions

3. **Gmail Authentication Issues**
   - Ensure your Gmail OAuth credentials are properly set up
   - Check that the refresh token hasn't expired

4. **Airtable Connection Issues**
   - Verify your Airtable API key and base ID
   - Check that the table name matches exactly

### Debug Mode
Add `--debug` to any command for more verbose output:
```bash
python main.py --max-leads 2 --debug
```

## Testing Checklist

- [ ] Apollo API fetches 2 leads successfully
- [ ] Caching works (second run uses cache)
- [ ] AI enrichment generates scores and emails for 2 leads
- [ ] Airtable is updated with 2 new records
- [ ] Email generation creates personalized content
- [ ] Send queue can read 1 pending email
- [ ] Dry run shows expected email
- [ ] Actual email sending works for 1 email
- [ ] Airtable is updated after sending
- [ ] **Scale up to 5 leads** (only after everything works!)
- [ ] **Scale up to 10+ leads** (only after 5 leads work!)

## Next Steps

Once local testing is successful with 2 contacts:
1. Test with 5 contacts
2. Test with 10+ contacts
3. Deploy to AWS Lambda using `serverless deploy`
4. Test the Lambda function with a small batch
5. Monitor logs and performance
6. Scale up gradually

## Cost Optimization

- **Apollo API**: Start with 2 contacts, use caching to minimize calls
- **OpenAI**: The current setup uses GPT-3.5-turbo (cheaper than GPT-4)
- **Airtable**: Free tier includes 1,200 records per base
- **Gmail**: Free with OAuth setup

## Notes

- The cache expires after 24 hours by default
- You can adjust cache settings in `apollo_api.py`
- All scripts include proper error handling and logging
- The system is designed to be idempotent (safe to run multiple times)
- **Start small, scale gradually!**
