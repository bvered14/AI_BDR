from typing import List, Dict, Any
from config import Config

class LeadProcessor:
    def __init__(self):
        self.industry_weights = {
            'technology': 1.0,
            'software': 1.0,
            'saas': 1.0,
            'cybersecurity': 0.9,
            'fintech': 0.8,
            'healthcare': 0.7,
            'ecommerce': 0.7,
            'manufacturing': 0.6,
            'consulting': 0.5,
            'retail': 0.4,
            'education': 0.4,
            'non-profit': 0.3
        }
        
        self.region_weights = {
            'North America': 1.0,
            'Europe': 0.9,
            'Other': 0.5
        }
    
    def calculate_industry_score(self, industry: str) -> float:
        """
        Calculate industry relevance score
        """
        if not industry:
            return 0.5
        
        industry_lower = industry.lower()
        
        # Check for exact matches first
        for key, weight in self.industry_weights.items():
            if key in industry_lower:
                return weight
        
        # Check for partial matches
        for key, weight in self.industry_weights.items():
            if any(word in industry_lower for word in key.split()):
                return weight * 0.8
        
        return 0.3  # Default score for unknown industries
    
    def calculate_company_size_score(self, company_size: int) -> float:
        """
        Calculate company size score (prefer mid-size companies)
        """
        if not company_size or company_size == 0:
            return 0.5
        
        # Optimal range: 100-300 employees
        if 100 <= company_size <= 300:
            return 1.0
        elif 50 <= company_size < 100:
            return 0.8
        elif 300 < company_size <= 500:
            return 0.7
        else:
            return 0.3
    
    def calculate_region_score(self, region: str) -> float:
        """
        Calculate region score
        """
        return self.region_weights.get(region, 0.5)
    
    def calculate_total_score(self, lead: Dict[str, Any]) -> float:
        """
        Calculate total lead score based on all criteria
        """
        industry_score = self.calculate_industry_score(lead.get('company_industry', ''))
        company_size_score = self.calculate_company_size_score(lead.get('company_size', 0))
        region_score = self.calculate_region_score(lead.get('region', ''))
        
        total_score = (
            industry_score * Config.INDUSTRY_WEIGHT +
            company_size_score * Config.COMPANY_SIZE_WEIGHT +
            region_score * Config.REGION_WEIGHT
        )
        
        return round(total_score, 3)
    
    def rank_leads(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank leads by their total score
        """
        print("Processing and ranking leads...")
        
        for lead in leads:
            lead['score'] = self.calculate_total_score(lead)
            lead['industry_score'] = self.calculate_industry_score(lead.get('company_industry', ''))
            lead['company_size_score'] = self.calculate_company_size_score(lead.get('company_size', 0))
            lead['region_score'] = self.calculate_region_score(lead.get('region', ''))
        
        # Sort by score in descending order
        ranked_leads = sorted(leads, key=lambda x: x['score'], reverse=True)
        
        print(f"Ranked {len(ranked_leads)} leads")
        return ranked_leads
    
    def filter_high_quality_leads(self, leads: List[Dict[str, Any]], 
                                 min_score: float = 0.6) -> List[Dict[str, Any]]:
        """
        Filter leads based on minimum score threshold
        """
        high_quality_leads = [lead for lead in leads if lead['score'] >= min_score]
        print(f"Filtered to {len(high_quality_leads)} high-quality leads (score >= {min_score})")
        return high_quality_leads
    
    def get_lead_summary(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for the leads
        """
        if not leads:
            return {}
        
        # Calculate scores
        scores = [lead.get('score', 0) for lead in leads]
        regions = [lead.get('region', 'Unknown') for lead in leads]
        industries = [lead.get('company_industry', 'Unknown') for lead in leads]
        company_sizes = [lead.get('company_size', 0) for lead in leads]
        
        # Count regions
        region_counts = {}
        for region in regions:
            region_counts[region] = region_counts.get(region, 0) + 1
        
        # Count industries
        industry_counts = {}
        for industry in industries:
            industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        # Sort industries by count and get top 5
        top_industries = dict(sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        
        # Count company sizes
        size_50_100 = sum(1 for size in company_sizes if 50 <= size <= 100)
        size_100_300 = sum(1 for size in company_sizes if 100 <= size <= 300)
        size_300_500 = sum(1 for size in company_sizes if 300 <= size <= 500)
        
        summary = {
            'total_leads': len(leads),
            'average_score': round(sum(scores) / len(scores), 3) if scores else 0,
            'top_score': round(max(scores), 3) if scores else 0,
            'bottom_score': round(min(scores), 3) if scores else 0,
            'regions': region_counts,
            'industries': top_industries,
            'company_sizes': {
                '50-100': size_50_100,
                '100-300': size_100_300,
                '300-500': size_300_500
            }
        }
        
        return summary
    
    def process_leads(self, leads: List[Dict[str, Any]], 
                     min_score: float = 0.6) -> List[Dict[str, Any]]:
        """
        Main method to process, rank, and filter leads
        """
        print(f"Processing {len(leads)} leads...")
        
        # Rank leads
        ranked_leads = self.rank_leads(leads)
        
        # Filter high-quality leads
        filtered_leads = self.filter_high_quality_leads(ranked_leads, min_score)
        
        # Generate summary
        summary = self.get_lead_summary(filtered_leads)
        print("Lead Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        return filtered_leads
