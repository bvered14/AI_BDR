# GTM Lead Generation Pipeline

A complete Python MVP for automated B2B lead generation, processing, and outreach using Apollo API, OpenAI, Airtable, and Gmail.

## 🚀 Features

- **Lead Fetching**: Automatically fetch B2B leads from Apollo API based on job titles, company size, and regions
- **Lead Processing**: Rank and score leads based on industry relevance, company size, and region
- **Data Storage**: Push ranked leads to Airtable with automatic formatting
- **AI-Powered Outreach**: Generate personalized outreach emails using OpenAI GPT-4
- **Email Automation**: Send personalized emails via Gmail API with rate limiting

## 📋 Pipeline Overview

1. **Fetch B2B leads** from Apollo API (CTO, Head of Security; 50-500 employees; North America + Europe)
2. **Process and rank** leads based on industry relevance, company size, and region
3. **Push ranked leads** into Airtable
4. **Generate personalized emails** using OpenAI API
5. **Send emails** via Gmail API

## 🛠️ Setup

### Prerequisites

- Python 3.8+
- Apollo API key
- OpenAI API key
- Airtable API key and base ID
- Gmail account for sending emails

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI_BDR
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env with your API keys
   ```

5. **Configure API keys in `.env`**
   ```
   APOLLO_API_KEY=your_apollo_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   AIRTABLE_PAT=your_airtable_personal_access_token_here
   AIRTABLE_BASE_ID=your_airtable_base_id_here
   AIRTABLE_TABLE_NAME=Leads
   SENDER_EMAIL=your_email@gmail.com
   ```

### Airtable Setup

1. **Create an Airtable Account**
   - Go to [Airtable](https://airtable.com/) and create an account
   - Create a new base or use an existing one

2. **Get Your Personal Access Token**
   - Go to your [Airtable Account](https://airtable.com/account)
   - Generate a new Personal Access Token
   - Copy the token to your `.env` file as `AIRTABLE_PAT`

3. **Get Your Base ID**
   - Open your Airtable base
   - The base ID is in the URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
   - Copy the `appXXXXXXXXXXXXXX` part as your base ID

4. **Create a Table**
   - Create a table named "Leads" (or update `AIRTABLE_TABLE_NAME` in config)
   - The table will be automatically populated with the correct fields

### Google Cloud Setup (for Gmail only)

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Gmail API**
   - Enable Gmail API only (Google Sheets API no longer needed)

## 💾 Caching System

The pipeline includes a smart caching system to save Apollo API credits during development and testing:

### How It Works

- **Automatic Caching**: Apollo API responses are automatically cached locally
- **Cache Expiry**: Cache expires after 24 hours (configurable)
- **Smart Loading**: Subsequent runs use cached data instead of hitting the API
- **Force Refresh**: Option to bypass cache when needed

### Cache Management

```bash
# Check cache status
python main.py --cache-status

# Clear cache
python main.py --clear-cache

# Force refresh (ignore cache)
python main.py --force-refresh

# Or use the dedicated cache manager
python cache_manager.py status
python cache_manager.py clear
python cache_manager.py info
```

### Cache Benefits

- **Save API Credits**: No repeated API calls during development
- **Faster Testing**: Instant results from cache
- **Offline Development**: Work without internet connection
- **Cost Control**: Perfect for MVP development and testing

### Cache Files

- `cache/apollo_leads_cache.json` - Cached lead data
- `cache/apollo_cache_metadata.json` - Cache metadata and expiry info

## 🚀 Usage

### Basic Usage

```bash
# Run the complete pipeline (fetch, process, email)
python main.py

# Run with custom parameters
python main.py --max-leads 20 --min-score 0.7

# Preview emails without sending
python main.py --preview-only

# Skip email sending
python main.py --no-email

# Run demo with sample data (no API calls)
python main.py --demo
```

### Command Line Options

- `--max-leads N`: Maximum number of leads to fetch (default: 10)
- `--min-score S`: Minimum score threshold for leads (default: 0.6)
- `--preview-only`: Only preview emails without sending
- `--no-email`: Skip email sending
- `--demo`: Run in demo mode with sample data

### Example Run

```bash
# Run demo first to test the pipeline
python main.py --demo

# Run with 5 leads, minimum score 0.7, preview only
python main.py --max-leads 5 --min-score 0.7 --preview-only

# Full pipeline run
python main.py --max-leads 10
```

## 📁 Project Structure

```
AI_BDR/
├── main.py              # Main pipeline orchestrator
├── config.py            # Configuration and environment variables
├── apollo_api.py        # Apollo API integration
├── process_leads.py     # Lead processing and ranking
├── airtable_api.py      # Airtable integration
├── outreach.py          # OpenAI email generation
├── email_sender.py      # Gmail email sending
├── requirements.txt     # Python dependencies
├── env_example.txt      # Environment variables template
└── README.md           # This file
```

## 🔧 Configuration

### Lead Generation Settings

Edit `config.py` to customize:

- **Job Titles**: `['CTO', 'Head of Security', 'Chief Technology Officer', 'VP of Engineering']`
- **Company Size**: 50-500 employees
- **Regions**: `['North America', 'Europe']`
- **Scoring Weights**: Industry (40%), Company Size (30%), Region (30%)

### Email Settings

- **Subject Line**: "Quick question about your tech stack"
- **Model**: GPT-4 (configurable)
- **Max Tokens**: 500
- **Temperature**: 0.7

## 📊 Lead Scoring

Leads are scored based on:

1. **Industry Relevance** (40% weight)
   - Technology/Software/SaaS: 1.0
   - Cybersecurity: 0.9
   - Fintech: 0.8
   - Healthcare/E-commerce: 0.7
   - Manufacturing: 0.6
   - Others: 0.3-0.5

2. **Company Size** (30% weight)
   - 100-300 employees: 1.0 (optimal)
   - 50-100 employees: 0.8
   - 300-500 employees: 0.7

3. **Region** (30% weight)
   - North America: 1.0
   - Europe: 0.9
   - Other: 0.5

## 🔒 Security

- All API keys are stored in environment variables
- No hardcoded credentials in the code
- Google OAuth 2.0 for secure authentication
- Rate limiting implemented for API calls

## 🐛 Troubleshooting

### Common Issues

1. **Missing API Keys**
   ```
   Error: Missing required environment variables
   ```
   Solution: Check your `.env` file and ensure all required variables are set

2. **Google Authentication Issues**
   ```
   Error: Credentials file not found
   ```
   Solution: Download the correct credentials files from Google Cloud Console

3. **Apollo API Rate Limiting**
   ```
   Error: Rate limit exceeded
   ```
   Solution: The pipeline includes built-in rate limiting (1 second between requests)

4. **Gmail Authentication**
   ```
   Error: Gmail authentication failed
   ```
   Solution: Ensure your Gmail account has 2FA enabled and use an App Password

### Debug Mode

Run with verbose logging:
```bash
python main.py --demo  # Test with sample data first
```

## 📈 Example Output

```
============================================================
GTM LEAD GENERATION PIPELINE
============================================================

1. Validating configuration...
✓ Configuration validated

2. Fetching up to 10 leads from Apollo API...
Fetching page 1 from Apollo API...
✓ Fetched 8 leads from Apollo API

3. Processing and ranking leads (min score: 0.6)...
Processing and ranking leads...
Ranked 8 leads
Filtered to 6 high-quality leads (score >= 0.6)
Lead Summary:
  total_leads: 6
  average_score: 0.783
  top_score: 0.92
  bottom_score: 0.61
✓ Processed and ranked 6 leads

4. Pushing leads to Airtable...
Successfully wrote batch of 6 records to Airtable
Total records written to Airtable: 6
✓ Successfully pushed leads to Airtable

5. Generating personalized outreach emails...
Generating personalized emails for 6 leads...
✓ Generated 6 personalized emails

6. Sending 6 emails via Gmail...
Sending email 1/6 to John Smith (john.smith@techcorp.com)
Email sent successfully to john.smith@techcorp.com
✓ Sent 6/6 emails successfully

============================================================
PIPELINE COMPLETED SUCCESSFULLY
============================================================
Execution time: 45.23 seconds
Leads fetched: 8
Leads processed: 6
Emails generated: 6
Emails sent: 6
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Run the demo mode first: `python main.py --demo`
3. Review the configuration in `config.py`
4. Check your API keys and credentials

## 🔄 Future Enhancements

- [ ] Add CRM integration (Salesforce, HubSpot)
- [ ] Implement email tracking and analytics
- [ ] Add A/B testing for email templates
- [ ] Create web dashboard for monitoring
- [ ] Add more lead sources (LinkedIn, ZoomInfo)
- [ ] Implement lead nurturing sequences