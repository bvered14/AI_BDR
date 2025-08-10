from typing import List, Dict, Any
from .config import Config

class LeadProcessor:
    def __init__(self):
        # Exposed weights for transparency and easy tweaking
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
        
        # Company size scoring ranges
        self.size_ranges = {
            '50-100': (50, 100, 0.8),
            '100-300': (100, 300, 1.0),
            '300-500': (300, 500, 0.7)
        }
    
    def calculate_industry_score(self, industry: str) -> tuple[float, str]:
        """
        Calculate industry relevance score and return reason
        """
        if not industry:
            return 0.5, "industry:unknown"
        
        industry_lower = industry.lower()
        
        # Check for exact matches first
        for key, weight in self.industry_weights.items():
            if key in industry_lower:
                return weight, f"industry:{key}"
        
        # Check for partial matches
        for key, weight in self.industry_weights.items():
            if any(word in industry_lower for word in key.split()):
                return weight * 0.8, f"industry:{key}(partial)"
        
        return 0.3, "industry:unknown"
    
    def calculate_company_size_score(self, company_size: int) -> tuple[float, str]:
        """
        Calculate company size score and return reason
        """
        if not company_size or company_size == 0:
            return 0.5, "size:unknown"
        
        # Check size ranges
        for range_name, (min_size, max_size, weight) in self.size_ranges.items():
            if min_size <= company_size <= max_size:
                return weight, f"size:{range_name}"
        
        # Outside preferred ranges
        if company_size < 50:
            return 0.3, "size:too-small"
        else:
            return 0.3, "size:too-large"
    
    def calculate_region_score(self, region: str) -> tuple[float, str]:
        """
        Calculate region score and return reason
        """
        weight = self.region_weights.get(region, 0.5)
        return weight, f"region:{region.lower()}"
    
    def calculate_total_score(self, lead: Dict[str, Any]) -> tuple[float, List[str]]:
        """
        Calculate total lead score and return reasons
        """
        industry_score, industry_reason = self.calculate_industry_score(lead.get('company_industry', ''))
        company_size_score, size_reason = self.calculate_company_size_score(lead.get('company_size', 0))
        region_score, region_reason = self.calculate_region_score(lead.get('region', ''))
        
        total_score = (
            industry_score * Config.INDUSTRY_WEIGHT +
            company_size_score * Config.COMPANY_SIZE_WEIGHT +
            region_score * Config.REGION_WEIGHT
        )
        
        # Build reasons list
        reasons = []
        if industry_score > 0.7:
            reasons.append(f"+{industry_reason}")
        if company_size_score > 0.7:
            reasons.append(f"+{size_reason}")
        if region_score > 0.7:
            reasons.append(f"+{region_reason}")
        
        return round(total_score, 3), reasons
    
    def rank_leads(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank leads by their total score with transparency
        """
        print("Processing and ranking leads...")
        
        for lead in leads:
            score, reasons = self.calculate_total_score(lead)
            lead['score'] = score
            lead['score_reasons'] = reasons
            lead['industry_score'] = self.calculate_industry_score(lead.get('company_industry', ''))[0]
            lead['company_size_score'] = self.calculate_company_size_score(lead.get('company_size', 0))[0]
            lead['region_score'] = self.calculate_region_score(lead.get('region', ''))[0]
        
        # Sort by score in descending order
        ranked_leads = sorted(leads, key=lambda x: x['score'], reverse=True)
        
        # Print scoring transparency
        print(f"\n📊 Scoring Summary:")
        print(f"   Industry Weight: {Config.INDUSTRY_WEIGHT}")
        print(f"   Company Size Weight: {Config.COMPANY_SIZE_WEIGHT}")
        print(f"   Region Weight: {Config.REGION_WEIGHT}")
        
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
