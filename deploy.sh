#!/bin/bash

echo "🚀 Deploying BDR Lead Pipeline to AWS Lambda (Cheapest MVP)"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if serverless is installed
if ! command -v serverless &> /dev/null; then
    echo "📦 Installing serverless framework..."
    npm install -g serverless
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Set up AWS credentials (if not already set)
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "🔑 Please configure your AWS credentials:"
    aws configure
fi

# Store API keys in AWS Systems Manager Parameter Store
echo "🔐 Setting up API keys in AWS Parameter Store..."

# Apollo API Key
read -p "Enter your Apollo API Key: " APOLLO_API_KEY
aws ssm put-parameter \
    --name "/bdr-pipeline/apollo-api-key" \
    --value "$APOLLO_API_KEY" \
    --type "SecureString" \
    --overwrite

# OpenAI API Key
read -p "Enter your OpenAI API Key: " OPENAI_API_KEY
aws ssm put-parameter \
    --name "/bdr-pipeline/openai-api-key" \
    --value "$OPENAI_API_KEY" \
    --type "SecureString" \
    --overwrite

# Airtable Personal Access Token
read -p "Enter your Airtable Personal Access Token: " AIRTABLE_PAT
aws ssm put-parameter \
    --name "/bdr-pipeline/airtable-pat" \
    --value "$AIRTABLE_PAT" \
    --type "SecureString" \
    --overwrite

# Airtable Base ID
read -p "Enter your Airtable Base ID: " AIRTABLE_BASE_ID
aws ssm put-parameter \
    --name "/bdr-pipeline/airtable-base-id" \
    --value "$AIRTABLE_BASE_ID" \
    --type "SecureString" \
    --overwrite

# Sender Email
read -p "Enter your sender email: " SENDER_EMAIL
aws ssm put-parameter \
    --name "/bdr-pipeline/sender-email" \
    --value "$SENDER_EMAIL" \
    --type "SecureString" \
    --overwrite

# Deploy to AWS
echo "🚀 Deploying to AWS Lambda..."
serverless deploy

echo "✅ Deployment complete!"
echo ""
echo "📋 Your pipeline is now running at:"
echo "   - Daily schedule: 9 AM UTC"
echo "   - Manual trigger: Use the API endpoint shown above"
echo ""
echo "💰 Estimated monthly cost: $5-15 (depending on usage)"
echo ""
echo "🔧 To test the pipeline:"
echo "   npm run invoke"
echo ""
echo "📊 To view logs:"
echo "   npm run logs"
