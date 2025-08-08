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
        
        try:
            response = requests.post(
                f"{self.base_url}/people/search",
                headers=self.headers,
                json=search_params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching leads from Apollo: {e}")
            return {"people": [], "pagination": {}}
    
    def get_company_info(self, organization_id: str) -> Dict[str, Any]:
        """
        Get detailed company information
        """
        params = {
            "api_key": self.api_key,
            "id": organization_id
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/organizations/{organization_id}",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching company info: {e}")
            return {}
    
    def fetch_leads(self, max_leads: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch leads with all criteria and return processed lead data
        """
        all_leads = []
        page = 1
        
        while len(all_leads) < max_leads:
            print(f"Fetching page {page} from Apollo API...")
            
            response = self.search_people(
                job_titles=Config.JOB_TITLES,
                company_size_min=Config.COMPANY_SIZE_MIN,
                company_size_max=Config.COMPANY_SIZE_MAX,
                regions=Config.REGIONS,
                page=page,
                per_page=25
            )
            
            if not response.get("people"):
                break
            
            for person in response["people"]:
                if len(all_leads) >= max_leads:
                    break
                
                # Get company details
                org_id = person.get("organization", {}).get("id")
                company_info = {}
                if org_id:
                    company_info = self.get_company_info(org_id)
                
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
                
                all_leads.append(lead_data)
            
            page += 1
            time.sleep(1)  # Rate limiting
        
        print(f"Fetched {len(all_leads)} leads from Apollo API")
        return all_leads[:max_leads]
    
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
