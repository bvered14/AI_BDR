"""
Tests for the Apollo API module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bdr_ai.apollo_api import ApolloAPI


class TestApolloAPI:
    """Test cases for the ApolloAPI class."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch.dict('os.environ', {'APOLLO_API_KEY': 'test_key'}):
            self.api = ApolloAPI()

    def test_initialization(self):
        """Test ApolloAPI initialization."""
        assert self.api.api_key == 'test_key'
        assert 'X-Api-Key' in self.api.headers
        assert self.api.headers['X-Api-Key'] == 'test_key'
        assert self.api.base_url == 'https://api.apollo.io/v1'

    def test_cache_initialization(self):
        """Test cache initialization."""
        assert hasattr(self.api, 'cache_dir')
        assert hasattr(self.api, 'cache_file')
        assert hasattr(self.api, 'cache_metadata_file')
        assert self.api.cache_enabled is True

    def test_make_request_success(self):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        
        with patch('requests.request', return_value=mock_response):
            result = self.api._make_request('GET', '/test')
            assert result == {'data': 'test'}

    def test_make_request_retry_on_failure(self):
        """Test retry mechanism on API failure."""
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {'data': 'success'}
        
        with patch('requests.request', side_effect=[mock_response_fail, mock_response_success]):
            result = self.api._make_request('GET', '/test')
            assert result == {'data': 'success'}

    def test_make_request_max_retries_exceeded(self):
        """Test behavior when max retries are exceeded."""
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch('requests.request', return_value=mock_response):
            result = self.api._make_request('GET', '/test')
            assert result is None

    def test_search_people_parameters(self):
        """Test search_people method parameters."""
        with patch.object(self.api, '_make_request') as mock_request:
            self.api.search_people(
                job_titles=['CEO'],
                company_size_min=10,
                company_size_max=1000,
                regions=['North America'],
                page=1,
                per_page=25
            )
            
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == 'POST'
            assert 'people/search' in call_args[0][1]

    def test_get_company_info(self):
        """Test get_company_info method."""
        with patch.object(self.api, '_make_request') as mock_request:
            self.api.get_company_info('test_org_id')
            
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == 'GET'
            assert 'organizations/test_org_id' in call_args[0][1]

    def test_cache_operations(self):
        """Test cache operations."""
        # Test cache save
        test_data = [{'id': 1, 'name': 'Test Lead'}]
        self.api._save_to_cache(test_data)
        
        # Test cache load
        loaded_data = self.api._load_from_cache()
        assert loaded_data == test_data

    def test_cache_validation(self):
        """Test cache validation."""
        # Test valid cache
        self.api._save_to_cache([{'test': 'data'}])
        assert self.api._is_cache_valid() is True
        
        # Test expired cache
        with patch.object(self.api, 'cache_expiry_hours', 0):
            assert self.api._is_cache_valid() is False

    def test_clear_cache(self):
        """Test cache clearing."""
        # Add some data to cache
        self.api._save_to_cache([{'test': 'data'}])
        
        # Clear cache
        self.api.clear_cache()
        
        # Verify cache is empty
        loaded_data = self.api._load_from_cache()
        assert loaded_data == []

    def test_process_person_to_lead(self):
        """Test lead processing from person data."""
        person_data = {
            'id': '123',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'title': 'CEO',
            'organization': {
                'id': '456',
                'name': 'Test Company',
                'industry': 'Technology'
            }
        }
        
        company_info = {
            'organization': {
                'size_range': '10-50',
                'location': 'San Francisco, CA'
            }
        }
        
        lead = self.api._process_person_to_lead(person_data, company_info)
        
        assert lead['name'] == 'John Doe'
        assert lead['email'] == 'john@example.com'
        assert lead['title'] == 'CEO'
        assert lead['company'] == 'Test Company'

    def test_determine_region(self):
        """Test region determination logic."""
        # Test North America
        assert self.api._determine_region('San Francisco, CA') == 'North America'
        assert self.api._determine_region('New York, NY') == 'North America'
        
        # Test Europe
        assert self.api._determine_region('London, UK') == 'Europe'
        assert self.api._determine_region('Berlin, Germany') == 'Europe'
        
        # Test Other
        assert self.api._determine_region('Tokyo, Japan') == 'Other'
