# 🎯 Setup Checklist - BDR Lead Pipeline

## ✅ **What You Have**
- ✅ Complete Python codebase
- ✅ All high-impact fixes implemented
- ✅ Lambda deployment configuration
- ✅ Documentation and READMEs
- ✅ Environment validation
- ✅ Preview mode (safe testing)

## 🔑 **What You Need**

### **1. API Keys (Required)**
- [ ] **Apollo API Key**
  - Sign up at [Apollo.io](https://apollo.io/)
  - Get API key from dashboard
  - Add to `.env`: `APOLLO_API_KEY=your_key`

- [ ] **OpenAI API Key**
  - Sign up at [OpenAI](https://platform.openai.com/)
  - Get API key from dashboard
  - Add to `.env`: `OPENAI_API_KEY=your_key`

- [ ] **Airtable Setup**
  - Create account at [Airtable](https://airtable.com/)
  - Create new base
  - Get Base ID from URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
  - Get Personal Access Token from [Account Settings](https://airtable.com/account)
  - Add to `.env`:
    ```
    AIRTABLE_PAT=your_personal_access_token_here
    AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
    AIRTABLE_TABLE_NAME=Leads
    ```

- [ ] **Sender Email**
  - Add to `.env`: `SENDER_EMAIL=your_email@gmail.com`

### **2. Optional: Gmail Setup (For Email Sending)**
- [ ] **Google Cloud Project**
  - Create at [Google Cloud Console](https://console.cloud.google.com/)
  - Enable Gmail API
  - Create OAuth 2.0 credentials
  - Download as `gmail_credentials.json`

- [ ] **Gmail Authentication**
  - Run Gmail setup (first time only)
  - Generates `gmail_token.json`

### **3. Optional: AWS Lambda Deployment**
- [ ] **AWS CLI**
  - Install AWS CLI
  - Configure with `aws configure`

- [ ] **Node.js/npm**
  - Install Node.js and npm
  - Install Serverless Framework: `npm install -g serverless`

## 🚀 **Quick Start Commands**

### **Local Testing**
```bash
# 1. Create environment file
cp env_example.txt .env

# 2. Edit .env with your API keys
# (Just the 5 required ones)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test locally (preview mode)
python main.py --demo
```

### **Lambda Deployment**
```bash
# 1. Run deployment script
chmod +x deploy.sh
./deploy.sh

# 2. Follow prompts for API keys
# 3. Deploy to AWS Lambda
```

## 🎯 **Priority Order**

### **Phase 1: Basic Functionality** (5 minutes)
1. Get Apollo API key
2. Get OpenAI API key  
3. Create Airtable base
4. Test locally with `python main.py --demo`

### **Phase 2: Email Sending** (15 minutes)
1. Set up Google Cloud Project
2. Configure Gmail OAuth
3. Test email sending

### **Phase 3: Production Deployment** (30 minutes)
1. Set up AWS CLI
2. Deploy to Lambda
3. Configure scheduling

## 📊 **Current Status**

| Component | Status | Priority |
|-----------|--------|----------|
| **Codebase** | ✅ Complete | - |
| **Apollo API** | ⏳ Need key | High |
| **OpenAI API** | ⏳ Need key | High |
| **Airtable** | ⏳ Need setup | High |
| **Gmail** | ⏳ Optional | Medium |
| **AWS Lambda** | ⏳ Optional | Low |

## 🎉 **You're 90% Ready!**

**Just need the API keys and you can start testing immediately!**

The hardest part (coding) is done. The remaining setup is just:
1. **5 minutes**: Get API keys
2. **5 minutes**: Create Airtable base
3. **5 minutes**: Test locally

**Total time to MVP: ~15 minutes** 🚀
