# AWS Lambda Deployment Guide

This guide covers deploying the BDR AI pipeline to AWS Lambda for serverless execution.

## 🚀 Quick Deploy

### Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Serverless Framework** installed
4. **Node.js** (for Serverless Framework)

### Install Dependencies

```bash
# Install Serverless Framework
npm install -g serverless

# Install project dependencies
pip install -r requirements.txt
```

### Deploy to AWS

```bash
# Deploy all functions
serverless deploy

# Deploy specific function
serverless deploy function --function fetch-leads
```

## 📋 Lambda Functions

The pipeline is split into multiple Lambda functions for modular execution:

### 1. **fetch-leads**
- **Purpose**: Fetch leads from Apollo API
- **Trigger**: Manual or scheduled
- **Output**: Stores leads in Airtable

### 2. **process-leads**
- **Purpose**: Process and score leads
- **Trigger**: After fetch-leads completes
- **Output**: Updates lead scores in Airtable

### 3. **generate-emails**
- **Purpose**: Generate personalized emails using OpenAI
- **Trigger**: After process-leads completes
- **Output**: Creates email records in Airtable

### 4. **send-emails**
- **Purpose**: Send emails via Gmail API
- **Trigger**: Manual or scheduled
- **Output**: Updates email status in Airtable

### 5. **run-pipeline**
- **Purpose**: Orchestrate the entire pipeline
- **Trigger**: Manual or scheduled
- **Output**: Coordinates all functions

## ⚙️ Configuration

### Environment Variables

Set these in your `serverless.yml` or AWS Lambda console:

```env
# API Keys
APOLLO_API_KEY=your_apollo_api_key
OPENAI_API_KEY=your_openai_api_key

# Airtable Configuration
AIRTABLE_PAT=your_airtable_pat
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLES=["Companies", "Contacts", "Emails"]

# Gmail Configuration
SENDER_EMAIL=your_email@gmail.com
GMAIL_CREDENTIALS_FILE=credentials/gmail_credentials.json
GMAIL_TOKEN_FILE=credentials/gmail_token.json

# Pipeline Configuration
MAX_LEADS_TO_PROCESS=5
JOB_TITLES=["VP Engineering", "CTO", "Head of DevOps"]
COMPANY_SIZE_MIN=10
COMPANY_SIZE_MAX=1000
REGIONS=["North America", "Europe"]
```

### Gmail Credentials Setup

1. **Create Gmail API credentials** in Google Cloud Console
2. **Download credentials** as JSON file
3. **Upload to Lambda** or store in AWS Secrets Manager

```bash
# Upload credentials to Lambda
aws lambda update-function-configuration \
  --function-name bdr-ai-dev-send-emails \
  --environment Variables='{"GMAIL_CREDENTIALS":"base64_encoded_credentials"}'
```

## 🛠️ Deployment Steps

### Step 1: Prepare Credentials

```bash
# Create credentials directory
mkdir -p credentials

# Add your Gmail credentials
cp path/to/gmail_credentials.json credentials/
cp path/to/gmail_token.json credentials/
```

### Step 2: Configure Serverless

Update `serverless.yml` with your settings:

```yaml
service: bdr-ai

provider:
  name: aws
  runtime: python3.9
  region: us-east-1
  environment:
    APOLLO_API_KEY: ${env:APOLLO_API_KEY}
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}
    AIRTABLE_PAT: ${env:AIRTABLE_PAT}
    AIRTABLE_BASE_ID: ${env:AIRTABLE_BASE_ID}
    SENDER_EMAIL: ${env:SENDER_EMAIL}
    MAX_LEADS: 5

functions:
  fetch-leads:
    handler: lambda_functions/fetch_leads.handler
    events:
      - schedule: rate(1 day)
  
  send-emails:
    handler: lambda_functions/send_emails.handler
    events:
      - schedule: rate(1 hour)
```

### Step 3: Deploy

```bash
# Deploy to AWS
serverless deploy

# Check deployment status
serverless info
```

## 🧪 Testing Lambda Functions

### Local Testing

```bash
# Test locally with Serverless
serverless invoke local --function fetch-leads

# Test with sample event
serverless invoke local --function send-emails --path test-event.json
```

### AWS Testing

```bash
# Test deployed function
aws lambda invoke \
  --function-name bdr-ai-dev-fetch-leads \
  --payload '{"test": true}' \
  response.json
```

### Monitor Logs

```bash
# View CloudWatch logs
serverless logs --function fetch-leads --tail

# Or use AWS CLI
aws logs tail /aws/lambda/bdr-ai-dev-fetch-leads --follow
```

## 📊 Monitoring & Alerting

### CloudWatch Metrics

Monitor these key metrics:
- **Invocation count** - Function execution frequency
- **Duration** - Execution time
- **Error rate** - Failed executions
- **Throttles** - Rate limit issues

### Set Up Alerts

```yaml
# Add to serverless.yml
resources:
  Resources:
    ErrorAlarm:
      Type: AWS::CloudWatch::Alarm
      Properties:
        AlarmName: bdr-ai-error-alarm
        MetricName: Errors
        Namespace: AWS/Lambda
        Statistic: Sum
        Period: 300
        EvaluationPeriods: 1
        Threshold: 1
        ComparisonOperator: GreaterThanOrEqualToThreshold
```

## 🔧 Troubleshooting

### Common Issues

#### 1. **Import Errors**
```bash
# Ensure all dependencies are in requirements.txt
pip freeze > requirements.txt

# Check Lambda layer includes all packages
serverless deploy --verbose
```

#### 2. **Timeout Issues**
```yaml
# Increase timeout in serverless.yml
functions:
  fetch-leads:
    handler: lambda_functions/fetch_leads.handler
    timeout: 300  # 5 minutes
```

#### 3. **Memory Issues**
```yaml
# Increase memory allocation
functions:
  generate-emails:
    handler: lambda_functions/generate_emails.handler
    memorySize: 1024  # 1GB
```

#### 4. **Permission Errors**
```yaml
# Add IAM permissions
provider:
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
          Resource: "*"
```

### Debug Mode

```bash
# Enable debug logging
export SLS_DEBUG=*

# Deploy with verbose output
serverless deploy --verbose
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS Lambda

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          npm install -g serverless
      
      - name: Deploy to AWS
        run: serverless deploy
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## 💰 Cost Optimization

### Strategies

1. **Reserved Concurrency**: Set limits to prevent runaway costs
2. **Scheduled Execution**: Use CloudWatch Events for predictable timing
3. **Memory Optimization**: Right-size memory allocation
4. **Cold Start Reduction**: Use provisioned concurrency for critical functions

### Cost Monitoring

```bash
# Check Lambda costs
aws ce get-cost-and-usage \
  --time-period Start=2023-01-01,End=2023-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

## 🔒 Security Best Practices

### Secrets Management

```yaml
# Use AWS Secrets Manager
provider:
  environment:
    APOLLO_API_KEY: ${ssm:/bdr-ai/apollo-api-key}
    OPENAI_API_KEY: ${ssm:/bdr-ai/openai-api-key}
```

### VPC Configuration

```yaml
# Deploy in VPC for enhanced security
provider:
  vpc:
    securityGroupIds:
      - sg-xxxxxxxxxxxxxxxxx
    subnetIds:
      - subnet-xxxxxxxxxxxxxxxxx
      - subnet-xxxxxxxxxxxxxxxxx
```

## 📈 Scaling Considerations

### Auto Scaling

```yaml
# Configure auto scaling
functions:
  fetch-leads:
    handler: lambda_functions/fetch_leads.handler
    reservedConcurrency: 10
    provisionedConcurrency: 2
```

### Performance Tuning

1. **Memory**: Increase for CPU-intensive tasks
2. **Timeout**: Set appropriate timeouts
3. **Concurrency**: Limit concurrent executions
4. **Caching**: Use Lambda layers for dependencies

---

**Next Steps**: After deployment, test the functions and set up monitoring. See [Local Testing Guide](LOCAL_TESTING.md) for testing procedures.
