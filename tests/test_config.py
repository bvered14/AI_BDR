"""
Tests for the configuration module.
"""

import os
import pytest
from unittest.mock import patch
from bdr_ai.config import Config


class TestConfig:
    """Test cases for the Config class."""

    def test_required_environment_variables(self):
        """Test that all required environment variables are defined."""
        required_vars = [
            'APOLLO_API_KEY',
            'OPENAI_API_KEY', 
            'AIRTABLE_PAT',
            'AIRTABLE_BASE_ID',
            'SENDER_EMAIL'
        ]
        
        for var in required_vars:
            assert hasattr(Config, var), f"Missing required environment variable: {var}"

    def test_validate_required_success(self):
        """Test successful validation of required environment variables."""
        with patch.dict(os.environ, {
            'APOLLO_API_KEY': 'test_apollo_key',
            'OPENAI_API_KEY': 'test_openai_key',
            'AIRTABLE_PAT': 'test_airtable_pat',
            'AIRTABLE_BASE_ID': 'test_base_id',
            'SENDER_EMAIL': 'test@example.com'
        }):
            # Should not raise an exception
            Config.validate_required()

    def test_validate_required_missing_variable(self):
        """Test validation fails when required variable is missing."""
        with patch.dict(os.environ, {
            'APOLLO_API_KEY': 'test_apollo_key',
            'OPENAI_API_KEY': 'test_openai_key',
            'AIRTABLE_PAT': 'test_airtable_pat',
            'AIRTABLE_BASE_ID': 'test_base_id',
            # Missing SENDER_EMAIL
        }, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variable"):
                Config.validate_required()

    def test_default_values(self):
        """Test that default values are properly set."""
        assert Config.MAX_LEADS_TO_PROCESS == 5
        assert Config.OPENAI_MODEL == "gpt-3.5-turbo"
        assert isinstance(Config.JOB_TITLES, list)
        assert isinstance(Config.REGIONS, list)

    def test_airtable_tables_config(self):
        """Test Airtable tables configuration."""
        expected_tables = ["Companies", "Contacts", "Emails"]
        assert Config.AIRTABLE_TABLES == expected_tables

    def test_scoring_weights(self):
        """Test that scoring weights are properly configured."""
        assert hasattr(Config, 'INDUSTRY_WEIGHT')
        assert hasattr(Config, 'COMPANY_SIZE_WEIGHT')
        assert hasattr(Config, 'REGION_WEIGHT')
        
        # Weights should be positive numbers
        assert Config.INDUSTRY_WEIGHT > 0
        assert Config.COMPANY_SIZE_WEIGHT > 0
        assert Config.REGION_WEIGHT > 0
