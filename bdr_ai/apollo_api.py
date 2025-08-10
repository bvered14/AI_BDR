import requests
import time
import json
import pathlib
from typing import List, Dict, Any
from .config import Config

class ApolloAPI:
    def __init__(self):
        self.api_key = Config.APOLLO_API_KEY
        self.base_url = Config.APOLLO_BASE_URL
        self.headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }
        self.timeout = 30
        self.max_retries = 3
        self.retry_delay = 1
        
        # Cache configuration
        self.cache_dir = pathlib.Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "apollo_leads_cache.json"
        self.cache_metadata_file = self.cache_dir / "apollo_cache_metadata.json"
        
        # Cache settings
        self.cache_enabled = True
        self.cache_expiry_hours = 24  # Cache expires after 24 hours
    
    def _is_cache_valid(self) -> bool:
        """
        Check if the cache is still valid (not expired)
        """
        if not self.cache_metadata_file.exists():
            return False
        
        try:
            with open(self.cache_metadata_file, 'r') as f:
                metadata = json.load(f)
            
            cache_time = metadata.get('timestamp', 0)
            current_time = time.time()
            cache_age_hours = (current_time - cache_time) / 3600
            
            return cache_age_hours < self.cache_expiry_hours
        except Exception as e:
            print(f"⚠️ Error reading cache metadata: {e}")
            return False
    
    def _load_from_cache(self) -> List[Dict[str, Any]]:
        """
        Load leads from cache if available and valid
        """
        if not self.cache_enabled or not self.cache_file.exists():
            return []
        
        if not self._is_cache_valid():
            print("🔄 Cache expired, will fetch fresh data")
            return []
        
        try:
            with open(self.cache_file, 'r') as f:
                cached_leads = json.load(f)
            print(f"📁 Loaded {len(cached_leads)} leads from cache")
            return cached_leads
        except Exception as e:
            print(f"⚠️ Error loading from cache: {e}")
            return []
    
    def _save_to_cache(self, leads: List[Dict[str, Any]]) -> None:
        """
        Save leads to cache with metadata
        """
        if not self.cache_enabled:
            return
        
        try:
            # Save leads data
            with open(self.cache_file, 'w') as f:
                json.dump(leads, f, ensure_ascii=False, indent=2)
            
            # Save cache metadata
            metadata = {
                'timestamp': time.time(),
                'leads_count': len(leads),
                'cache_expiry_hours': self.cache_expiry_hours,
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(self.cache_metadata_file, 'w') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Cached {len(leads)} leads for future use")
        except Exception as e:
            print(f"⚠️ Error saving to cache: {e}")
    
    def clear_cache(self) -> None:
        """
        Clear the cache files
        """
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
                print("🗑️ Cleared leads cache")
            
            if self.cache_metadata_file.exists():
                self.cache_metadata_file.unlink()
                print("🗑️ Cleared cache metadata")
        except Exception as e:
            print(f"⚠️ Error clearing cache: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the current cache
        """
        if not self.cache_metadata_file.exists():
            return {'status': 'no_cache'}
        
        try:
            with open(self.cache_metadata_file, 'r') as f:
                metadata = json.load(f)
            
            cache_time = metadata.get('timestamp', 0)
            current_time = time.time()
            cache_age_hours = (current_time - cache_time) / 3600
            
            return {
                'status': 'valid' if cache_age_hours < self.cache_expiry_hours else 'expired',
                'leads_count': metadata.get('leads_count', 0),
                'cache_age_hours': round(cache_age_hours, 2),
                'expires_in_hours': round(self.cache_expiry_hours - cache_age_hours, 2),
                'created_at': metadata.get('created_at', 'Unknown')
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def set_cache_settings(self, enabled: bool = None, expiry_hours: int = None) -> None:
        """
        Update cache settings
        """
        if enabled is not None:
            self.cache_enabled = enabled
            print(f"💾 Cache {'enabled' if enabled else 'disabled'}")
        
        if expiry_hours is not None:
            self.cache_expiry_hours = expiry_hours
            print(f"⏰ Cache expiry set to {expiry_hours} hours")
    
    def print_cache_status(self) -> None:
        """
        Print current cache status in a user-friendly format
        """
        cache_info = self.get_cache_info()
        
        print("\n📁 Apollo API Cache Status:")
        print("=" * 40)
        
        if cache_info['status'] == 'no_cache':
            print("❌ No cache found")
            print("   First run will fetch from Apollo API")
        elif cache_info['status'] == 'valid':
            print(f"✅ Cache is valid")
            print(f"   📊 Cached leads: {cache_info['leads_count']}")
            print(f"   ⏰ Cache age: {cache_info['cache_age_hours']} hours")
            print(f"   🔄 Expires in: {cache_info['expires_in_hours']} hours")
            print(f"   📅 Created: {cache_info['created_at']}")
        elif cache_info['status'] == 'expired':
            print(f"🔄 Cache expired")
            print(f"   📊 Cached leads: {cache_info['leads_count']}")
            print(f"   ⏰ Cache age: {cache_info['cache_age_hours']} hours")
            print(f"   📅 Created: {cache_info['created_at']}")
            print(f"   ⚠️ Will fetch fresh data on next run")
        else:
            print(f"❌ Cache error: {cache_info.get('error', 'Unknown error')}")
        
        print(f"💾 Cache enabled: {self.cache_enabled}")
        print(f"⏰ Expiry setting: {self.cache_expiry_hours} hours")
        print("=" * 40)
    
    def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request with retries and timeout
        """
        for attempt in range(self.max_retries):
            try:
                kwargs.setdefault('timeout', self.timeout)
                response = requests.request(method, url, headers=self.headers, **kwargs)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    print(f"❌ Failed after {self.max_retries} attempts: {e}")
                    return {}
                else:
                    print(f"⚠️ Attempt {attempt + 1} failed, retrying in {self.retry_delay}s: {e}")
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 2  # Exponential backoff
        
        return {}
    
    def search_people(self, job_titles: List[str], company_size_min: int, 
                     company_size_max: int, regions: List[str], 
                     page: int = 1, per_page: int = 25) -> Dict[str, Any]:
        """
        Search for people using Apollo API with specified criteria
        """
        # Use minimal parameters to avoid 422 errors
        search_params = {
            "page": page,
            "per_page": per_page
        }
        
        # Add job titles if provided
        if job_titles:
            search_params["q_titles"] = job_titles
        
        return self._make_request(
            'POST',
            f"{self.base_url}/people/search",
            json=search_params
        )
    
    def search_contacts(self, page: int = 1, per_page: int = 25) -> Dict[str, Any]:
        """
        Search for contacts in your Apollo contact list
        Based on Apollo API documentation: https://docs.apollo.io/reference/people-search
        """
        search_params = {
            "page": page,
            "per_page": per_page
        }
        
        return self._make_request(
            'POST',
            f"{self.base_url}/contacts/search",
            json=search_params
        )
    
    def get_company_info(self, organization_id: str) -> Dict[str, Any]:
        """
        Get detailed company information
        """
        params = {
            "id": organization_id
        }
        
        return self._make_request(
            'GET',
            f"{self.base_url}/organizations/{organization_id}",
            params=params
        )
    
    def fetch_leads(self, max_leads: int = 10, force_refresh: bool = False, use_contact_list: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch leads with pagination until max_leads is reached
        Uses cache if available and valid, unless force_refresh is True
        """
        # Check cache first (unless force refresh is requested)
        if not force_refresh:
            cached_leads = self._load_from_cache()
            if cached_leads:
                # Return cached leads up to the requested max
                return cached_leads[:max_leads]
        
        # If no cache or force refresh, fetch from API
        if use_contact_list:
            print(f"📋 Fetching up to {max_leads} contacts from your Apollo contact list...")
        else:
            print(f"🔍 Fetching up to {max_leads} leads from Apollo API...")
        
        all_leads = []
        page = 1
        per_page = min(25, max_leads)  # Don't fetch more than needed
        
        while len(all_leads) < max_leads:
            print(f"   📄 Fetching page {page}...")
            
            if use_contact_list:
                response = self.search_contacts(page=page, per_page=per_page)
                contacts = response.get("contacts", [])
                if not contacts:
                    print(f"   ✅ No more contacts found (page {page})")
                    break
                
                print(f"   📊 Found {len(contacts)} contacts on page {page}")
                
                for contact in contacts:
                    if len(all_leads) >= max_leads:
                        break
                    
                    # Get company details if available
                    org_id = contact.get("organization", {}).get("id")
                    company_info = {}
                    if org_id:
                        company_info = self.get_company_info(org_id)
                    
                    # Process and add lead
                    lead = self._process_contact_to_lead(contact, company_info)
                    if lead:
                        all_leads.append(lead)
            else:
                response = self.search_people(
                    job_titles=Config.JOB_TITLES,
                    company_size_min=Config.COMPANY_SIZE_MIN,
                    company_size_max=Config.COMPANY_SIZE_MAX,
                    regions=Config.REGIONS,
                    page=page,
                    per_page=per_page
                )
                
                people = response.get("people", [])
                if not people:
                    print(f"   ✅ No more results found (page {page})")
                    break
                
                print(f"   📊 Found {len(people)} people on page {page}")
                
                for person in people:
                    if len(all_leads) >= max_leads:
                        break
                    
                    # Get company details
                    org_id = person.get("organization", {}).get("id")
                    company_info = {}
                    if org_id:
                        company_info = self.get_company_info(org_id)
                    
                    # Process and add lead
                    lead = self._process_person_to_lead(person, company_info)
                    if lead:
                        all_leads.append(lead)
            
            # Check if we have more pages
            pagination = response.get("pagination", {})
            if not pagination.get("has_more", False):
                print(f"   ✅ No more pages available")
                break
            
            page += 1
            time.sleep(0.5)  # Rate limiting between pages
        
        print(f"✅ Successfully fetched {len(all_leads)} leads")
        
        # Cache the results for future use
        if all_leads:
            self._save_to_cache(all_leads)
        
        return all_leads
    
    def _process_person_to_lead(self, person: Dict[str, Any], company_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single person object to create a lead dictionary.
        """
        if not person:
            return {}
        
        lead_data = {
            "first_name": person.get("first_name", ""),
            "last_name": person.get("last_name", ""),
            "email": person.get("email", ""),
            "title": person.get("title", ""),
            "company_name": person.get("organization", {}).get("name", ""),
            "company_size": person.get("organization", {}).get("employee_count", 0),
            "company_industry": person.get("organization", {}).get("industry", ""),
            "company_location": person.get("organization", {}).get("location", ""),
            "linkedin_url": person.get("linkedin_url", ""),
            "apollo_id": person.get("id", ""),
            "company_domain": person.get("organization", {}).get("domain", ""),
            "company_revenue": company_info.get("organization", {}).get("estimated_annual_revenue", ""),
            "company_founded": company_info.get("organization", {}).get("founded_year", ""),
            "region": self._determine_region(person.get("organization", {}).get("location", ""))
        }
        
        return lead_data
    
    def _process_contact_to_lead(self, contact: Dict[str, Any], company_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a contact from Apollo contact list into a standardized lead format
        """
        if not contact:
            return {}
        
        lead_data = {
            "first_name": contact.get("first_name", ""),
            "last_name": contact.get("last_name", ""),
            "email": contact.get("email", ""),
            "title": contact.get("title", ""),
            "company_name": contact.get("organization", {}).get("name", ""),
            "company_size": contact.get("organization", {}).get("employee_count", 0),
            "company_industry": contact.get("organization", {}).get("industry", ""),
            "company_location": contact.get("organization", {}).get("location", ""),
            "linkedin_url": contact.get("linkedin_url", ""),
            "apollo_id": contact.get("id", ""),
            "company_domain": contact.get("organization", {}).get("domain", ""),
            "company_revenue": company_info.get("organization", {}).get("estimated_annual_revenue", ""),
            "company_founded": company_info.get("organization", {}).get("founded_year", ""),
            "region": self._determine_region(contact.get("organization", {}).get("location", ""))
        }
        
        return lead_data
    
    def _determine_region(self, location: str) -> str:
        """
        Determine region based on location
        """
        if not location:
            return "Unknown"
        
        location_lower = location.lower()
        
        # North America
        na_countries = ["united states", "usa", "canada", "mexico"]
        if any(country in location_lower for country in na_countries):
            return "North America"
        
        # Europe
        eu_countries = ["united kingdom", "uk", "germany", "france", "spain", "italy", 
                       "netherlands", "sweden", "norway", "denmark", "finland", 
                       "switzerland", "austria", "belgium", "ireland"]
        if any(country in location_lower for country in eu_countries):
            return "Europe"
        
        return "Other"
    
    def _calculate_lead_score(self, person: Dict[str, Any], company_info: Dict[str, Any]) -> float:
        """
        Calculate a lead score based on configurable weights
        """
        score = 0.0
        
        # Industry scoring
        industry = person.get("organization", {}).get("industry", "").lower()
        if industry in ["technology", "software", "saas", "fintech", "healthtech"]:
            score += Config.INDUSTRY_WEIGHT
        
        # Company size scoring
        company_size = person.get("organization", {}).get("employee_count", 0)
        if Config.COMPANY_SIZE_MIN <= company_size <= Config.COMPANY_SIZE_MAX:
            score += Config.COMPANY_SIZE_WEIGHT
        
        # Region scoring
        region = self._determine_region(person.get("organization", {}).get("location", ""))
        if region in Config.REGIONS:
            score += Config.REGION_WEIGHT
        
        return min(score, 1.0)  # Cap at 1.0
