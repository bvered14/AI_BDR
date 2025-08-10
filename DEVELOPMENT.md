# BDR AI - Development Guide

## 🎯 **Design Patterns and Coding Paradigms**

### **1. Object-Oriented Design**
- **Single Responsibility Principle**: Each class has one clear purpose
- **Dependency Injection**: Components receive dependencies through constructors
- **Factory Pattern**: Used for creating API clients and processors
- **Strategy Pattern**: Different scoring algorithms and email templates

### **2. Functional Programming Elements**
- **Pure Functions**: Scoring and processing functions are stateless
- **Immutable Data**: Lead data structures are not modified in place
- **Higher-Order Functions**: Map, filter, reduce for data processing

### **3. Error Handling Patterns**
- **Fail Fast**: Validate configuration early
- **Graceful Degradation**: Continue processing even if some components fail
- **Retry Logic**: Exponential backoff for API calls
- **Circuit Breaker**: Prevent cascading failures

## 📋 **PEP 8 Compliance**

### **Code Style**
```python
# ✅ Good
def calculate_lead_score(lead_data: Dict[str, Any]) -> float:
    """Calculate lead score based on multiple factors."""
    industry_score = _get_industry_score(lead_data['industry'])
    size_score = _get_size_score(lead_data['company_size'])
    region_score = _get_region_score(lead_data['region'])
    
    return (industry_score * Config.INDUSTRY_WEIGHT +
            size_score * Config.COMPANY_SIZE_WEIGHT +
            region_score * Config.REGION_WEIGHT)

# ❌ Bad
def calculateLeadScore(leadData):
    industryScore=getIndustryScore(leadData['industry'])
    sizeScore=getSizeScore(leadData['company_size'])
    regionScore=getRegionScore(leadData['region'])
    return industryScore*Config.INDUSTRY_WEIGHT+sizeScore*Config.COMPANY_SIZE_WEIGHT+regionScore*Config.REGION_WEIGHT
```

### **Import Organization**
```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Third-party imports
import requests
import pandas as pd
import numpy as np
from openai import OpenAI

# Local imports
from .config import Config
from .utils import helpers
```

## 🔬 **Scientific Python Stack Integration**

### **1. NumPy for Numerical Operations**
```python
import numpy as np

def calculate_weighted_score(scores: List[float], weights: List[float]) -> float:
    """Calculate weighted average using NumPy."""
    return np.average(scores, weights=weights)

def normalize_scores(scores: List[float]) -> np.ndarray:
    """Normalize scores to 0-1 range."""
    return (np.array(scores) - np.min(scores)) / (np.max(scores) - np.min(scores))
```

### **2. Pandas for Data Processing**
```python
import pandas as pd

def analyze_lead_data(leads: List[Dict]) -> pd.DataFrame:
    """Convert leads to DataFrame for analysis."""
    df = pd.DataFrame(leads)
    
    # Statistical analysis
    summary = df.groupby('region')['score'].agg(['mean', 'std', 'count'])
    
    # Data quality checks
    missing_data = df.isnull().sum()
    
    return df, summary, missing_data

def filter_leads_by_criteria(df: pd.DataFrame, 
                           min_score: float = 0.6,
                           regions: List[str] = None) -> pd.DataFrame:
    """Filter leads using pandas operations."""
    filtered = df[df['score'] >= min_score]
    
    if regions:
        filtered = filtered[filtered['region'].isin(regions)]
    
    return filtered.sort_values('score', ascending=False)
```

### **3. SciPy for Statistical Analysis**
```python
from scipy import stats

def analyze_lead_distribution(scores: List[float]) -> Dict:
    """Perform statistical analysis on lead scores."""
    scores_array = np.array(scores)
    
    return {
        'mean': np.mean(scores_array),
        'median': np.median(scores_array),
        'std': np.std(scores_array),
        'skewness': stats.skew(scores_array),
        'percentiles': np.percentile(scores_array, [25, 50, 75])
    }
```

### **4. Matplotlib/Seaborn for Visualization**
```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_lead_analysis(leads: List[Dict]):
    """Create comprehensive lead analysis plots."""
    df = pd.DataFrame(leads)
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Score distribution
    sns.histplot(data=df, x='score', bins=20, ax=axes[0, 0])
    axes[0, 0].set_title('Lead Score Distribution')
    
    # Scores by region
    sns.boxplot(data=df, x='region', y='score', ax=axes[0, 1])
    axes[0, 1].set_title('Scores by Region')
    
    # Company size vs score
    sns.scatterplot(data=df, x='company_size', y='score', ax=axes[1, 0])
    axes[1, 0].set_title('Company Size vs Score')
    
    # Industry distribution
    df['industry'].value_counts().plot(kind='bar', ax=axes[1, 1])
    axes[1, 1].set_title('Leads by Industry')
    
    plt.tight_layout()
    plt.savefig('lead_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
```

### **5. Scikit-learn for Machine Learning**
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

def build_lead_classifier(leads: List[Dict]) -> RandomForestClassifier:
    """Build ML model to predict lead quality."""
    df = pd.DataFrame(leads)
    
    # Feature engineering
    features = ['company_size', 'score', 'region_encoded']
    X = df[features]
    y = (df['score'] > 0.7).astype(int)  # High-quality leads
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    print(classification_report(y_test, y_pred))
    
    return model, scaler
```

## 🧪 **Testing Strategy**

### **1. Unit Tests**
```python
import pytest
from unittest.mock import Mock, patch
from bdr_ai.process_leads import LeadProcessor

class TestLeadProcessor:
    """Test cases for LeadProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = LeadProcessor()
        self.sample_lead = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'company': 'TechCorp',
            'industry': 'Software',
            'company_size': 150,
            'region': 'North America'
        }
    
    def test_calculate_total_score(self):
        """Test lead scoring calculation."""
        score, reasons = self.processor.calculate_total_score(self.sample_lead)
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert isinstance(reasons, list)
        assert len(reasons) > 0
    
    @pytest.mark.parametrize("industry,expected_score", [
        ("Software", 1.0),
        ("Cybersecurity", 0.9),
        ("Manufacturing", 0.6),
        ("Retail", 0.3)
    ])
    def test_industry_scoring(self, industry, expected_score):
        """Test industry scoring with different industries."""
        lead = self.sample_lead.copy()
        lead['industry'] = industry
        
        score, _ = self.processor.calculate_total_score(lead)
        assert abs(score - expected_score) < 0.1
```

### **2. Integration Tests**
```python
@pytest.mark.integration
class TestApolloIntegration:
    """Integration tests for Apollo API."""
    
    def test_fetch_leads_integration(self):
        """Test actual Apollo API integration."""
        apollo = ApolloAPI()
        leads = apollo.fetch_leads(max_leads=5)
        
        assert isinstance(leads, list)
        if leads:  # If API returns data
            assert all(isinstance(lead, dict) for lead in leads)
            assert 'name' in leads[0]
            assert 'email' in leads[0]
```

### **3. Performance Tests**
```python
import time
import pytest

@pytest.mark.slow
class TestPerformance:
    """Performance tests."""
    
    def test_lead_processing_performance(self):
        """Test processing performance with large dataset."""
        processor = LeadProcessor()
        
        # Generate test data
        test_leads = [
            {
                'name': f'Test User {i}',
                'email': f'user{i}@example.com',
                'company': f'Company {i}',
                'industry': 'Software',
                'company_size': 100 + i,
                'region': 'North America'
            }
            for i in range(1000)
        ]
        
        start_time = time.time()
        processed_leads = processor.process_leads(test_leads)
        end_time = time.time()
        
        processing_time = end_time - start_time
        assert processing_time < 5.0  # Should process 1000 leads in under 5 seconds
        assert len(processed_leads) > 0
```

## 📚 **Documentation Standards**

### **1. Docstring Format (Google Style)**
```python
def calculate_lead_score(lead_data: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Calculate comprehensive lead score based on multiple factors.
    
    This function evaluates lead quality using industry relevance, company size,
    geographic location, and other business factors to assign a score between
    0 and 1, where higher scores indicate better prospects.
    
    Args:
        lead_data: Dictionary containing lead information with keys:
            - industry: Company industry (str)
            - company_size: Number of employees (int)
            - region: Geographic region (str)
            - title: Job title (str)
            - company_revenue: Annual revenue range (str)
        
    Returns:
        Tuple containing:
            - score: Float between 0 and 1 representing lead quality
            - reasons: List of strings explaining scoring factors
        
    Raises:
        ValueError: If required lead_data fields are missing
        KeyError: If lead_data is missing expected keys
    
    Example:
        >>> lead = {
        ...     'industry': 'Software',
        ...     'company_size': 150,
        ...     'region': 'North America'
        ... }
        >>> score, reasons = calculate_lead_score(lead)
        >>> print(f"Score: {score:.2f}")
        Score: 0.85
        >>> print(f"Reasons: {reasons}")
        Reasons: ['High industry relevance', 'Optimal company size']
    """
```

### **2. Type Hints**
```python
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path

def process_leads(
    leads: List[Dict[str, Any]],
    min_score: float = 0.6,
    max_leads: Optional[int] = None,
    filters: Optional[Dict[str, Any]] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Process and filter leads based on scoring criteria."""
    pass
```

## 🔧 **Development Workflow**

### **1. Using the Development Script**
```bash
# Install development environment
python scripts/dev.py install-dev

# Run tests
python scripts/dev.py test

# Format code
python scripts/dev.py format

# Run all checks
python scripts/dev.py check

# Run pipeline
python scripts/dev.py run-pipeline
```

### **2. Pre-commit Hooks**
```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### **3. Code Quality Checks**
```bash
# Lint code
python scripts/dev.py lint

# Type checking
mypy bdr_ai/

# Security scanning
bandit -r bdr_ai/
```

## 📊 **Data Analysis and Visualization**

### **1. Jupyter Notebooks**
Create notebooks in `notebooks/` directory for:
- Lead analysis and insights
- Model development and evaluation
- Performance monitoring
- A/B testing results

### **2. Automated Reporting**
```python
def generate_weekly_report(leads: List[Dict]) -> str:
    """Generate automated weekly lead analysis report."""
    df = pd.DataFrame(leads)
    
    report = f"""
    # Weekly Lead Analysis Report
    
    ## Summary
    - Total leads processed: {len(df)}
    - Average score: {df['score'].mean():.2f}
    - Top performing region: {df.groupby('region')['score'].mean().idxmax()}
    
    ## Score Distribution
    {df['score'].describe().to_string()}
    
    ## Industry Breakdown
    {df['industry'].value_counts().to_string()}
    """
    
    return report
```

## 🚀 **Deployment and CI/CD**

### **1. GitHub Actions Workflow**
```yaml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          python scripts/dev.py test
      - name: Run linting
        run: |
          python scripts/dev.py lint
```

### **2. Docker Support**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["python", "main.py"]
```

This development guide ensures your BDR AI project follows industry best practices and is ready for professional deployment! 🎯
