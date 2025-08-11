# BDR AI - Business Development Representative Automation Tool

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/yourusername/bdr-ai/workflows/Tests/badge.svg)](https://github.com/yourusername/bdr-ai/actions)

A comprehensive B2B lead generation and outreach automation system that integrates Apollo API, Airtable, OpenAI, and Gmail to create personalized outreach campaigns. Built with extensible architecture to support additional data sources like LinkedIn Sales Navigator, Hunter.io, and more.

## 🚀 Features

- **Lead Generation**: Automated lead discovery from Apollo API
- **Data Management**: Centralized storage and management in Airtable
- **AI-Powered Emails**: Personalized outreach using OpenAI GPT models
- **Email Automation**: Automated sending via Gmail API
- **Lead Scoring**: Intelligent qualification and ranking of prospects
- **Caching**: Efficient API usage with intelligent caching
- **AWS Lambda**: Serverless deployment ready
- **Rate Limiting**: Built-in protection against API limits

## 🖼️ Demo

![BDR AI Platform Interface](docs/images/bdr-ai-interface.png)

*The BDR AI platform showing email generation and management in Airtable - emails are generated with personalized content and can be manually marked for sending*

## 📋 Requirements

- Python 3.8+
- Apollo API account
- Airtable account with Personal Access Token
- OpenAI API account
- Gmail account with API access
- AWS account (for Lambda deployment)

## 🛠️ Installation

### From PyPI (Coming Soon)
```bash
pip install bdr-ai
```

### From Source
```bash
git clone https://github.com/yourusername/bdr-ai.git
cd bdr-ai
pip install -e .
```

### Development Setup
```bash
git clone https://github.com/yourusername/bdr-ai.git
cd bdr-ai
pip install -e ".[dev]"
pre-commit install
```

## ⚙️ Configuration

1. **Copy the environment template:**
```bash
cp env_example.txt .env
```

2. **Fill in your API credentials:**
```env
# API Keys
APOLLO_API_KEY=your_apollo_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Airtable Configuration
AIRTABLE_PAT=your_airtable_personal_access_token_here
AIRTABLE_BASE_ID=your_airtable_base_id_here
AIRTABLE_TABLES=["Companies", "Contacts", "Emails"]

# Gmail Configuration
SENDER_EMAIL=your_email@gmail.com
GMAIL_CREDENTIALS_FILE=path/to/gmail_credentials.json
GMAIL_TOKEN_FILE=path/to/gmail_token.json

**Note:** App is in testing; add your account under OAuth consent → Test users to avoid the common 403 error. See [Gmail Setup Guide](README_LAMBDA.md) for detailed instructions.

# Pipeline Configuration
MAX_LEADS_TO_PROCESS=2
JOB_TITLES=["CTO", "Head of Security", "Chief Technology Officer", "VP of Engineering"]
COMPANY_SIZE_MIN=50
COMPANY_SIZE_MAX=500
REGIONS=["North America", "Europe"]
```

3. **Set up Airtable tables** (see [Airtable Setup Guide](MULTIPLE_TABLES_SETUP.md))

4. **Configure Gmail API** (see [Gmail Setup Guide](README_LAMBDA.md))

## 🚀 Quick Start

### Basic Usage

```python
from bdr_ai import ApolloAPI, AirtableAPI, OutreachGenerator, GmailSender

# Initialize components
apollo = ApolloAPI()
airtable = AirtableAPI()
email_gen = OutreachGenerator()
gmail = GmailSender()

# Complete pipeline: Apollo → Airtable → OpenAI → Airtable → Gmail
# 1. Fetch contacts from Apollo contact list
contacts = apollo.fetch_leads(max_leads=2, use_contact_list=True)

# 2. Store contacts in Airtable
airtable.push_contacts(contacts)

# 3. Generate personalized emails from Airtable contacts
emails = email_gen.generate_emails_from_airtable()

# 4. Send emails from Airtable (after marking them for sending)
gmail.send_emails_from_airtable()
```

### Command Line Interface

```bash
# Run the complete pipeline (Apollo → Airtable → OpenAI → Airtable → Gmail)
python main.py --max-leads 2

# Preview mode (no emails sent)
python main.py --max-leads 2 --preview-only

# Demo mode (sample data, no API calls)
python main.py --demo

# Send emails from Airtable (after marking them for sending)
python main.py --send-emails
```

## 📚 Documentation

- [Local Testing Guide](LOCAL_TESTING.md) - How to test locally
- [AWS Lambda Deployment](README_LAMBDA.md) - Serverless deployment
- [Airtable Setup](MULTIPLE_TABLES_SETUP.md) - Database configuration
- [Setup Checklist](SETUP_CHECKLIST.md) - Complete setup guide

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bdr_ai

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8

# Type checking
mypy bdr_ai/
```

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Apollo    │    │  Airtable   │    │   OpenAI    │    │    Gmail    │
│     API     │    │     API     │    │     API     │    │     API     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Lead Fetch │    │ Data Storage│    │Email Gen    │    │Email Send   │
│ & Scoring   │    │ & Management│    │ & Personal. │    │ & Tracking  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       └───────────────────┼───────────────────┼───────────────────┘
                           ▼
                   ┌─────────────┐
                   │   Main      │
                   │ Pipeline    │
                   └─────────────┘
```

## 📦 Project Structure

```
bdr-ai/
├── bdr_ai/                 # Main package
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── apollo_api.py      # Apollo API integration
│   ├── airtable_api.py    # Airtable integration
│   ├── email_sender.py    # Gmail integration
│   ├── outreach.py        # AI email generation
│   └── process_leads.py   # Lead processing
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_apollo_api.py
│   └── ...
├── lambda_functions/      # AWS Lambda functions
├── docs/                  # Documentation
├── setup.py              # Package setup
├── requirements.txt      # Dependencies
├── pytest.ini           # Test configuration
├── .pre-commit-config.yaml # Code quality hooks
└── README.md             # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests
- Add type hints
- Update documentation
- Run pre-commit hooks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Apollo](https://apollo.io/) for lead generation API
- [Airtable](https://airtable.com/) for data management
- [OpenAI](https://openai.com/) for AI-powered email generation
- [Google Gmail API](https://developers.google.com/gmail) for email sending

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/bdr-ai/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/bdr-ai/wiki)
- **Email**: bar@baronmor.com

---

**Made for B2B sales teams**