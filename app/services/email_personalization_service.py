"""
Email personalization service that integrates OpenAI with website scraping
"""
from typing import Dict, Any, Optional
from app.services.openai_service import OpenAIService
from app.services.website_service import WebsiteService
from app.core.database import get_db
from supabase import Client
import logging

logger = logging.getLogger(__name__)

class EmailPersonalizationService:
    """
    Service for generating personalized emails using OpenAI and website content
    """
    
    def __init__(self, db: Client):
        self.db = db
        self.openai_service = OpenAIService()
        self.website_service = WebsiteService(db)
    
    async def generate_email_for_lead(
        self,
        lead_id: str,
        email_type: str = "initial",
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate personalized email for a lead
        
        Args:
            lead_id: Lead UUID
            email_type: Type of email (initial, followup_5day, followup_10day)
            force_regenerate: Force regeneration even if email exists
        
        Returns:
            Dict with email subject, body, and metadata
        """
        try:
            # Get lead data
            lead_result = self.db.table("leads").select("*").eq("id", lead_id).execute()
            
            if not lead_result.data or len(lead_result.data) == 0:
                return {
                    "success": False,
                    "error": "Lead not found"
                }
            
            lead = lead_result.data[0]
            
            # Check if email already generated (unless force_regenerate)
            if not force_regenerate:
                existing_email = self.db.table("emails_sent").select("*").eq("lead_id", lead_id).eq("email_type", email_type).execute()
                if existing_email.data and len(existing_email.data) > 0:
                    logger.info(f"Using existing email for lead {lead_id}")
                    return {
                        "success": True,
                        "subject": existing_email.data[0].get("email_subject"),
                        "body": existing_email.data[0].get("email_body"),
                        "from_cache": True,
                        "is_personalized": existing_email.data[0].get("is_personalized", False)
                    }
            
            # Get website content if available
            company_domain = lead.get("company_domain")
            company_website_content = None
            website_scraped = False
            
            logger.info(f"🎯 PERSONALIZATION: Getting website content for domain: {company_domain}")
            
            if company_domain:
                # Try to get cached website content
                website_content = await self.website_service.get_website_content(company_domain)
                
                if website_content:
                    company_website_content = website_content.get("markdown", "")
                    if company_website_content and len(company_website_content.strip()) > 0:
                        website_scraped = True
                        logger.info(f"✅ PERSONALIZATION: Using cached website content for {company_domain} (length: {len(company_website_content)} chars)")
                    else:
                        logger.warning(f"⚠️ PERSONALIZATION: Cached content exists but is empty for {company_domain}")
                else:
                    # Try to scrape if we have website URL
                    company_website = lead.get("company_website")
                    if company_website or company_domain:
                        logger.info(f"🌐 PERSONALIZATION: No cache found, scraping website for {company_domain}")
                        scrape_result = await self.website_service.scrape_company_website(
                            company_domain=company_domain,
                            company_website=company_website
                        )
                        
                        if scrape_result.get("success"):
                            company_website_content = scrape_result.get("markdown", "")
                            if company_website_content and len(company_website_content.strip()) > 0:
                                website_scraped = True
                                logger.info(f"✅ PERSONALIZATION: Successfully scraped website for {company_domain} (length: {len(company_website_content)} chars)")
                            else:
                                logger.warning(f"⚠️ PERSONALIZATION: Scrape succeeded but content is empty for {company_domain}")
                        else:
                            logger.warning(f"⚠️ PERSONALIZATION: Failed to scrape website for {company_domain}: {scrape_result.get('error')}")
                    else:
                        logger.warning(f"⚠️ PERSONALIZATION: No website URL or domain to scrape for {company_domain}")
            else:
                logger.warning(f"⚠️ PERSONALIZATION: No company domain for lead {lead_id}, cannot personalize")
            
            # Generate email using OpenAI
            logger.info(f"🤖 PERSONALIZATION: Generating email with OpenAI (has_website_content: {bool(company_website_content)})")
            email_result = await self.openai_service.generate_personalized_email(
                lead_name=f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip() or lead.get('email', '').split('@')[0],
                lead_title=lead.get("title", ""),
                company_name=lead.get("company_name", ""),
                company_website_content=company_website_content,
                company_industry=lead.get("company_industry"),
                email_type=email_type
            )
            
            logger.info(f"🤖 PERSONALIZATION: OpenAI result - Success: {email_result.get('success')}, Is_personalized: {email_result.get('is_personalized')}")
            
            if email_result.get("success"):
                return {
                    "success": True,
                    "subject": email_result.get("subject"),
                    "body": email_result.get("body"),
                    "is_personalized": email_result.get("is_personalized", website_scraped),
                    "company_website_used": website_scraped,
                    "from_cache": False,
                    "email_type": email_type
                }
            else:
                # Fallback to default template
                logger.warning(f"OpenAI generation failed, using default template: {email_result.get('error')}")
                default_template = self.openai_service.get_default_template(
                    lead_name=f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip() or lead.get('email', '').split('@')[0],
                    lead_title=lead.get("title", ""),
                    company_name=lead.get("company_name", ""),
                    email_type=email_type
                )
                
                return {
                    "success": True,
                    "subject": default_template.get("subject"),
                    "body": default_template.get("body"),
                    "is_personalized": False,
                    "company_website_used": False,
                    "from_cache": False,
                    "email_type": email_type,
                    "used_default_template": True
                }
        
        except Exception as e:
            logger.error(f"Error generating email for lead {lead_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

