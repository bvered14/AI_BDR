import requests
import time
from typing import List, Dict, Any
from config import Config

class ApolloAPI:
    def __init__(self):
        self.api_key = Config.APOLLO_API_KEY
        self.base_url = Config.APOLLO_BASE_URL
        self.headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }
        self.timeout = 30
        self.max_retries = 3
        self.retry_delay = 1
    
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
        search_params = {
            "api_key": self.api_key,
            "page": page,
            "per_page": per_page,
            "q_organization_domains": [],
            "q_organization_locations": regions,
            "q_organization_size_ranges": [f"{company_size_min}-{company_size_max}"],
            "q_titles": job_titles,
            "person_titles": job_titles,
            "contact_email_status": ["verified"],
            "organization_domains": [],
            "person_locations": regions,
            "page_size": per_page
        }
        
        return self._make_request(
            'POST',
            f"{self.base_url}/people/search",
            json=search_params
        )
    
    def get_company_info(self, organization_id: str) -> Dict[str, Any]:
        """
        Get detailed company information
        """
        params = {
            "api_key": self.api_key,
            "id": organization_id
        }
        
        return self._make_request(
            'GET',
            f"{self.base_url}/organizations/{organization_id}",
            params=params
        )
    
    def fetch_leads(self, max_leads: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch leads with pagination until max_leads is reached
        """
        all_leads = []
        page = 1
        per_page = min(25, max_leads)  # Don't fetch more than needed
        
        print(f"🔍 Fetching up to {max_leads} leads from Apollo API...")
        
        while len(all_leads) < max_leads:
            print(f"   📄 Fetching page {page}...")
            
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
