from openai import OpenAI
from typing import Dict, Any, List
from config import Config

class OutreachGenerator:
    def __init__(self):
        # Initialize OpenAI client only if API key is available
        if Config.OPENAI_API_KEY:
            try:
                # For newer OpenAI library versions (1.3+)
                self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            except Exception as e:
                # Fallback for any initialization issues
                print(f"Warning: OpenAI client initialization issue: {e}")
                print("Will use fallback email generation instead")
                self.client = None
        else:
            self.client = None
        self.model = Config.OPENAI_MODEL
    
    def generate_personalized_email(self, lead: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate a personalized outreach email for a lead
        """
        try:
            # Check if OpenAI client is available
            if not self.client:
                print(f"No OpenAI API key available, using fallback email for {lead.get('email', 'unknown')}")
                return self._generate_fallback_email(lead)
            
            # Prepare context for the AI
            context = self._prepare_lead_context(lead)
            
            # Create the prompt
            prompt = self._create_email_prompt(context)
            
            # Generate email using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional BDR (Business Development Representative) writing personalized outreach emails. Your emails should be concise, professional, and personalized based on the recipient's role and company information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            email_content = response.choices[0].message.content.strip()
            
            # Parse the response to extract subject and body
            email_parts = self._parse_email_response(email_content)
            
            return {
                'subject': email_parts.get('subject', Config.EMAIL_SUBJECT),
                'body': email_parts.get('body', email_content),
                'lead_info': context
            }
            
        except Exception as e:
            print(f"Error generating email for {lead.get('email', 'unknown')}: {e}")
            return self._generate_fallback_email(lead)
    
    def _prepare_lead_context(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare context information about the lead
        """
        return {
            'first_name': lead.get('first_name', ''),
            'last_name': lead.get('last_name', ''),
            'title': lead.get('title', ''),
            'company_name': lead.get('company_name', ''),
            'company_industry': lead.get('company_industry', ''),
            'company_size': lead.get('company_size', ''),
            'company_location': lead.get('company_location', ''),
            'region': lead.get('region', ''),
            'linkedin_url': lead.get('linkedin_url', ''),
            'company_domain': lead.get('company_domain', ''),
            'company_revenue': lead.get('company_revenue', ''),
            'company_founded': lead.get('company_founded', '')
        }
    
    def _create_email_prompt(self, context: Dict[str, Any]) -> str:
        """
        Create a detailed prompt for email generation
        """
        prompt = f"""
Generate a personalized outreach email for the following prospect:

Name: {context['first_name']} {context['last_name']}
Title: {context['title']}
Company: {context['company_name']}
Industry: {context['company_industry']}
Company Size: {context['company_size']} employees
Location: {context['company_location']} ({context['region']})
LinkedIn: {context['linkedin_url']}

Requirements:
1. Keep the email under 150 words
2. Make it personal and relevant to their role and company
3. Include a specific value proposition
4. End with a clear call-to-action
5. Be professional but conversational
6. Reference their company or industry when possible

Format the response as:
Subject: [Email Subject]
Body: [Email Body]

Focus on how our solution can help {context['company_name']} based on their industry ({context['company_industry']}) and size ({context['company_size']} employees).
"""
        return prompt
    
    def _parse_email_response(self, response: str) -> Dict[str, str]:
        """
        Parse the AI response to extract subject and body
        """
        lines = response.split('\n')
        subject = Config.EMAIL_SUBJECT
        body = response
        
        for i, line in enumerate(lines):
            if line.lower().startswith('subject:'):
                subject = line.split(':', 1)[1].strip()
                # Remove the subject line from body
                body = '\n'.join(lines[i+1:]).strip()
                break
        
        return {
            'subject': subject,
            'body': body
        }
    
    def _generate_fallback_email(self, lead: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate a fallback email if AI generation fails
        """
        first_name = lead.get('first_name', 'there')
        company_name = lead.get('company_name', 'your company')
        title = lead.get('title', '')
        
        subject = f"Quick question about {company_name}'s tech stack"
        
        body = f"""Hi {first_name},

I hope this email finds you well. I came across {company_name} and was impressed by your work in the industry.

I'm reaching out because I believe our solution could help {company_name} optimize its technology infrastructure, especially given your role as {title}.

Would you be open to a brief 15-minute call to discuss how we've helped similar companies in your space?

Best regards,
[Your Name]
[Your Company]"""
        
        return {
            'subject': subject,
            'body': body,
            'lead_info': self._prepare_lead_context(lead)
        }
    
    def generate_emails_for_leads(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate personalized emails for a list of leads
        """
        emails = []
        
        for lead in leads:
            email_data = self.generate_personalized_email(lead)
            
            # Add lead information to email data
            email_data['lead'] = lead
            email_data['to_email'] = lead.get('email', '')
            email_data['to_name'] = f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()
            
            emails.append(email_data)
            
            # Preview mode: show email in console
            if Config.PREVIEW_ONLY:
                self.preview_email(lead, email_data)
        
        return emails
    
    def preview_email(self, lead: Dict[str, Any], email_data: Dict[str, Any]) -> None:
        """
        Preview email in console (for preview mode)
        """
        print(f"\n📧 EMAIL PREVIEW for {lead.get('first_name', '')} {lead.get('last_name', '')} ({lead.get('email', '')})")
        print(f"   Company: {lead.get('company_name', '')} ({lead.get('company_size', '')} employees)")
        print(f"   Title: {lead.get('title', '')}")
        print(f"   Score: {lead.get('score', 0)} - Reasons: {', '.join(lead.get('score_reasons', []))}")
        print(f"   Subject: {email_data.get('subject', 'No subject')}")
        print(f"   Body: {email_data.get('body', 'No body')[:200]}...")
        print("-" * 80)
