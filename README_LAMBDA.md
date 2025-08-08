# 🚀 BDR Lead Pipeline - AWS Lambda Deployment

**The cheapest MVP for automated B2B lead generation on AWS Lambda**

## 💰 **Cost Optimization**

This deployment is optimized for **minimum cost**:
- **Memory**: 256MB (minimum for most functions)
- **Timeout**: 5 minutes max
- **Region**: us-east-1 (cheapest)
- **Schedule**: Daily at 9 AM UTC (configurable)
- **Estimated monthly cost**: $5-15

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Daily Trigger │───▶│  Fetch Leads    │───▶│ Process Leads   │
│   (9 AM UTC)    │    │   (Apollo API)  │    │   (Scoring)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Manual API    │◀───│  Store Leads    │◀───│ Generate Emails │
│   Endpoint      │    │   (Airtable)    │    │   (OpenAI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                              ┌─────────────────┐
                                              │  Send Emails    │
                                              │   (Gmail API)   │
                                              └─────────────────┘
```

## 🚀 **Quick Deployment**

### **Prerequisites**
- AWS CLI installed and configured
- Node.js and npm
- Your API keys ready

### **1. Clone and Setup**
```bash
git clone <your-repo>
cd AI_BDR
chmod +x deploy.sh
```

### **2. Run Deployment**
```bash
./deploy.sh
```

The script will:
- Install dependencies
- Prompt for your API keys
- Store them securely in AWS Parameter Store
- Deploy all Lambda functions
- Set up daily scheduling

### **3. Test Your Pipeline**
```bash
# Test with 5 leads
npm run invoke

# View logs
npm run logs
```

## 📋 **Lambda Functions**

| Function | Memory | Timeout | Purpose |
|----------|--------|---------|---------|
| `fetch-leads` | 256MB | 60s | Apollo API calls |
| `process-leads` | 256MB | 30s | Lead scoring/ranking |
| `store-leads` | 256MB | 60s | Airtable storage |
| `generate-emails` | 512MB | 120s | OpenAI email generation |
| `send-emails` | 256MB | 120s | Gmail sending |
| `run-pipeline` | 256MB | 300s | Manual orchestrator |

## 🔧 **Configuration**

### **Environment Variables**
All API keys are stored securely in AWS Systems Manager Parameter Store:
- `/bdr-pipeline/apollo-api-key`
- `/bdr-pipeline/openai-api-key`
- `/bdr-pipeline/airtable-api-key`
- `/bdr-pipeline/airtable-base-id`
- `/bdr-pipeline/sender-email`

### **Customization**
Edit `serverless.yml` to modify:
- **Schedule**: Change `cron(0 9 * * ? *)` for different timing
- **Memory**: Adjust `memorySize` for performance/cost
- **Region**: Change `region` for different AWS regions
- **Timeout**: Modify `timeout` values

## 📊 **Monitoring & Logs**

### **View Logs**
```bash
# All functions
serverless logs

# Specific function
serverless logs -f fetch-leads

# Follow logs in real-time
serverless logs -f run-pipeline -t
```

### **CloudWatch Metrics**
Monitor in AWS Console:
- **Invocations**: Number of function calls
- **Duration**: Execution time
- **Errors**: Failed executions
- **Throttles**: Rate limiting

## 💡 **Usage Examples**

### **Manual Trigger**
```bash
# Trigger with custom parameters
aws lambda invoke \
  --function-name bdr-lead-pipeline-dev-run-pipeline \
  --payload '{"max_leads": 20, "min_score": 0.7}' \
  response.json
```

### **API Endpoint**
```bash
# POST to your API Gateway endpoint
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/run-pipeline \
  -H "Content-Type: application/json" \
  -d '{"max_leads": 10, "min_score": 0.6}'
```

## 🔒 **Security**

- **API Keys**: Stored in AWS Parameter Store (encrypted)
- **IAM Roles**: Minimal permissions required
- **VPC**: Not required (uses AWS Lambda default)
- **HTTPS**: All API Gateway endpoints use HTTPS

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Timeout Errors**
   ```bash
   # Increase timeout in serverless.yml
   timeout: 600  # 10 minutes
   ```

2. **Memory Errors**
   ```bash
   # Increase memory allocation
   memorySize: 512
   ```

3. **API Key Errors**
   ```bash
   # Check Parameter Store
   aws ssm get-parameter --name "/bdr-pipeline/apollo-api-key"
   ```

4. **Cold Start Issues**
   - Use provisioned concurrency (additional cost)
   - Or accept 1-2 second delays

### **Debug Mode**
```bash
# Enable detailed logging
serverless deploy --verbose

# Test individual functions
serverless invoke -f fetch-leads -d '{"max_leads": 1}'
```

## 💰 **Cost Breakdown**

| Component | Cost per 1000 leads |
|-----------|-------------------|
| **Lambda** | $0.50-2.00 |
| **API Gateway** | $0.10-0.50 |
| **CloudWatch Logs** | $0.50-1.00 |
| **Parameter Store** | $0.05 |
| **Total** | **$1.15-3.55** |

## 🚀 **Scaling**

### **Automatic Scaling**
- Lambda automatically scales based on demand
- No configuration needed
- Pay only for what you use

### **Manual Scaling**
```bash
# Increase concurrency
aws lambda put-function-concurrency \
  --function-name bdr-lead-pipeline-dev-fetch-leads \
  --reserved-concurrency-count 10
```

## 🔄 **Updates**

### **Deploy Updates**
```bash
# Deploy changes
serverless deploy

# Deploy specific function
serverless deploy function -f fetch-leads
```

### **Rollback**
```bash
# List versions
aws lambda list-versions-by-function --function-name bdr-lead-pipeline-dev-fetch-leads

# Rollback to previous version
aws lambda update-function-code --function-name bdr-lead-pipeline-dev-fetch-leads --zip-file fileb://previous-version.zip
```

## 📞 **Support**

For issues:
1. Check CloudWatch logs
2. Review function metrics
3. Test individual functions
4. Check API key permissions

---

**🎯 This is the cheapest possible MVP that will scale automatically and cost you less than $20/month for typical usage!**
