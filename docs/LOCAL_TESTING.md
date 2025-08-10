# Local Testing Guide

This guide walks you through testing the BDR AI pipeline locally before deploying to AWS Lambda.

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
# Install the package in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 2. **Set Up Environment**
```bash
# Copy environment template
cp config/env_example.txt .env

# Edit .env with your API keys
# (See config/env_example.txt for required variables)
```

### 3. **Test Individual Components**

#### **Test Apollo API**
```bash
# Check cache status
python utils/cache_manager.py status

# Clear cache (if needed)
python utils/cache_manager.py clear

# Test Apollo connection
python -c "from bdr_ai.apollo_api import ApolloAPI; apollo = ApolloAPI(); print('✅ Apollo API connected')"
```

#### **Test Airtable Connection**
```bash
python -c "from bdr_ai.airtable_api import AirtableAPI; airtable = AirtableAPI(); airtable.test_connection(); print('✅ Airtable connected')"
```

#### **Test OpenAI**
```bash
python -c "from bdr_ai.outreach import OutreachGenerator; gen = OutreachGenerator(); print('✅ OpenAI configured')"
```

#### **Test Gmail**
```bash
python -c "from bdr_ai.email_sender import GmailSender; gmail = GmailSender(); print('✅ Gmail configured')"
```

### 4. **Run Full Pipeline Test**

#### **Preview Mode (Recommended First)**
```bash
# Run pipeline in preview mode (no emails sent)
python main.py --max-leads 2 --preview-only
```

#### **Full Pipeline**
```bash
# Run complete pipeline with 2 leads
python main.py --max-leads 2
```

## 📋 Step-by-Step Testing

### **Step 1: Configuration Validation**
```bash
python -c "from bdr_ai.config import Config; Config.validate_required(); print('✅ Configuration valid')"
```

### **Step 2: Apollo Lead Fetching**
```bash
# Test with minimal leads
python main.py --max-leads 1 --no-email
```

**Expected Output:**
```
============================================================
BDR AI - LEAD GENERATION PIPELINE
============================================================

1. Validating configuration...
✓ Configuration validated

2. Initializing components...
✓ Components initialized

3. Fetching up to 1 leads from Apollo API...
✓ Fetched 1 leads from Apollo API

4. Processing and ranking leads (min score: 0.6)...
✓ Processed and ranked 1 leads

5. Storing leads in Airtable...
✓ Successfully stored leads in Airtable

6. Generating personalized outreach emails...
✓ Generated 1 personalized emails

7. Skipping email sending (--no-email flag)

============================================================
PIPELINE COMPLETED SUCCESSFULLY
============================================================
```

### **Step 3: Email Generation Test**
```bash
# Test email generation without sending
python main.py --max-leads 1 --preview-only
```

**Expected Output:**
```
7. Preview mode - emails not sent

--- Email 1 ---
To: john.doe@example.com
Subject: Quick question about your tech stack
Body: Hi John, I noticed you're the CTO at TechCorp...
```

### **Step 4: Email Sending Test**
```bash
# Send a single test email
python utils/send_queue.py --max 1
```

## 🔧 Troubleshooting

### **Common Issues**

#### **1. Import Errors**
```bash
# Make sure you're in the project root
cd /path/to/bdr-ai

# Install in development mode
pip install -e .
```

#### **2. Missing Environment Variables**
```bash
# Check if .env file exists
ls -la .env

# Copy template if missing
cp config/env_example.txt .env
```

#### **3. Apollo API Issues**
```bash
# Check API key
echo $APOLLO_API_KEY

# Test connection
python -c "from bdr_ai.apollo_api import ApolloAPI; apollo = ApolloAPI(); print(apollo.test_connection())"
```

#### **4. Airtable Connection Issues**
```bash
# Check credentials
echo $AIRTABLE_PAT
echo $AIRTABLE_BASE_ID

# Test connection
python -c "from bdr_ai.airtable_api import AirtableAPI; airtable = AirtableAPI(); airtable.test_connection()"
```

#### **5. Gmail Authentication Issues**
```bash
# Check credentials file
ls -la credentials/gmail_credentials.json

# Re-authenticate if needed
python -c "from bdr_ai.email_sender import GmailSender; gmail = GmailSender(); gmail.authenticate()"
```

## 📊 Testing Checklist

- [ ] **Environment Setup**
  - [ ] `.env` file configured
  - [ ] All API keys set
  - [ ] Dependencies installed

- [ ] **Component Testing**
  - [ ] Apollo API connection
  - [ ] Airtable connection
  - [ ] OpenAI configuration
  - [ ] Gmail authentication

- [ ] **Pipeline Testing**
  - [ ] Lead fetching (1-2 leads)
  - [ ] Lead processing and scoring
  - [ ] Airtable storage
  - [ ] Email generation
  - [ ] Email sending (optional)

- [ ] **Cache Testing**
  - [ ] Cache status check
  - [ ] Cache clearing
  - [ ] Cache validation

## 🎯 Performance Testing

### **Small Scale (Development)**
```bash
# Test with 1-2 leads
python main.py --max-leads 2
```

### **Medium Scale (Staging)**
```bash
# Test with 5-10 leads
python main.py --max-leads 10
```

### **Large Scale (Production)**
```bash
# Test with 50+ leads
python main.py --max-leads 50
```

## 📈 Monitoring

### **Log Analysis**
```bash
# Run with verbose logging
python main.py --max-leads 2 --verbose

# Check for errors
grep -i "error\|failed\|exception" logs/bdr_ai.log
```

### **Performance Metrics**
- **Lead Fetching**: Should complete in < 30 seconds for 10 leads
- **Email Generation**: Should complete in < 60 seconds for 10 emails
- **Email Sending**: Should complete in < 120 seconds for 10 emails

## 🚨 Error Recovery

### **If Pipeline Fails**
1. **Check logs** for specific error messages
2. **Validate configuration** with `Config.validate_required()`
3. **Test individual components** using the commands above
4. **Clear cache** if Apollo API issues: `python utils/cache_manager.py clear`
5. **Re-authenticate Gmail** if needed

### **If Emails Fail to Send**
1. **Check Gmail credentials** in `credentials/` folder
2. **Verify sender email** in `.env` file
3. **Test Gmail authentication**: `python -c "from bdr_ai.email_sender import GmailSender; gmail = GmailSender(); gmail.authenticate()"`

## ✅ Success Criteria

Your local testing is successful when:

1. **Pipeline runs without errors**
2. **Leads are fetched from Apollo**
3. **Data is stored in Airtable**
4. **Emails are generated with OpenAI**
5. **Emails can be sent via Gmail** (optional)

Once these criteria are met, you're ready to deploy to AWS Lambda! 🚀
