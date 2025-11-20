"""
Website scraping service that integrates Firecrawl with database caching
"""
from typing import Dict, Any, Optional
from app.services.firecrawl_service import FirecrawlService
from app.core.database import get_db
from supabase import Client
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebsiteService:
    """
    Service for scraping and caching company websites
    """
    
    def __init__(self, db: Client):
        self.db = db
        self.firecrawl = FirecrawlService()
    
    async def scrape_company_website(
        self,
        company_domain: str,
        company_website: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Scrape a company website, with caching to avoid re-scraping
        
        Args:
            company_domain: Company domain (e.g., "example.com")
            company_website: Full website URL (optional, will be constructed from domain if not provided)
        
        Returns:
            Dict containing scraped content and status
        """
        if not company_domain:
            return {
                "success": False,
                "error": "Company domain is required",
                "from_cache": False
            }
        
        # Check if already scraped (cache)
        existing = self.db.table("company_websites").select("*").eq("company_domain", company_domain).execute()
        
        if existing.data and len(existing.data) > 0:
            cached = existing.data[0]
            if cached.get("scraping_status") == "success":
                logger.info(f"Using cached website data for {company_domain}")
                return {
                    "success": True,
                    "from_cache": True,
                    "domain": company_domain,
                    "url": cached.get("website_url"),
                    "markdown": cached.get("scraped_content"),
                    "extracted_info": cached.get("extracted_info", {}),
                    "scraped_at": cached.get("scraped_at")
                }
        
        # Not in cache or failed before - scrape it
        # Normalize the URL - handle both domain and full URL cases
        if company_website:
            # If company_website is provided, use it (but normalize it)
            url = company_website
        else:
            # Build URL from domain
            # Remove any existing protocol from domain
            domain = company_domain.strip()
            if domain.startswith(("http://", "https://")):
                url = domain
            else:
                url = f"https://{domain}"
        
        # Ensure URL is properly formatted
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        # Create or update record with pending status
        website_record = {
            "company_domain": company_domain,
            "website_url": url,
            "scraping_status": "pending"
        }
        
        if existing.data and len(existing.data) > 0:
            # Update existing record
            record_id = existing.data[0]["id"]
            self.db.table("company_websites").update(website_record).eq("id", record_id).execute()
        else:
            # Create new record
            result = self.db.table("company_websites").insert(website_record).execute()
            record_id = result.data[0]["id"] if result.data else None
        
        try:
            # Scrape using Firecrawl
            logger.info(f"🌐 WEBSITE SERVICE: Calling Firecrawl to scrape {url} (domain: {company_domain})")
            scrape_result = await self.firecrawl.scrape_website(url)
            logger.info(f"🌐 WEBSITE SERVICE: Firecrawl returned - Success: {scrape_result.get('success')}, Error: {scrape_result.get('error', 'None')}")
            
            if scrape_result.get("success"):
                # Extract key information
                extracted_info = self.firecrawl.extract_key_info(
                    scrape_result.get("markdown", "")
                )
                
                # Update record with success
                markdown_content = scrape_result.get("markdown", "")
                logger.info(f"💾 WEBSITE SERVICE: Saving to DB - Content length: {len(markdown_content)} chars")
                
                update_data = {
                    "website_url": scrape_result.get("url"),
                    "scraped_content": markdown_content,
                    "extracted_info": extracted_info,
                    "scraping_status": "success",
                    "scraped_at": datetime.utcnow().isoformat(),
                    "scraping_error": None
                }
                
                self.db.table("company_websites").update(update_data).eq("id", record_id).execute()
                
                logger.info(f"✅ WEBSITE SERVICE: Successfully scraped and cached {company_domain} ({len(markdown_content)} chars saved)")
                
                return {
                    "success": True,
                    "from_cache": False,
                    "domain": company_domain,
                    "url": scrape_result.get("url"),
                    "markdown": scrape_result.get("markdown"),
                    "html": scrape_result.get("html"),
                    "extracted_info": extracted_info,
                    "metadata": scrape_result.get("metadata", {}),
                    "scraped_at": datetime.utcnow().isoformat()
                }
            else:
                # Update record with failure
                error_msg = scrape_result.get("error", "Unknown error")
                update_data = {
                    "scraping_status": "failed",
                    "scraping_error": error_msg,
                    "scraped_at": datetime.utcnow().isoformat()
                }
                
                if record_id:
                    self.db.table("company_websites").update(update_data).eq("id", record_id).execute()
                
                logger.warning(f"Failed to scrape {company_domain}: {error_msg}")
                
                return {
                    "success": False,
                    "from_cache": False,
                    "error": error_msg,
                    "domain": company_domain
                }
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error scraping {company_domain}: {error_msg}", exc_info=True)
            
            # Update record with error
            if record_id:
                update_data = {
                    "scraping_status": "failed",
                    "scraping_error": error_msg,
                    "scraped_at": datetime.utcnow().isoformat()
                }
                self.db.table("company_websites").update(update_data).eq("id", record_id).execute()
            
            return {
                "success": False,
                "from_cache": False,
                "error": error_msg,
                "domain": company_domain
            }
    
    async def get_website_content(self, company_domain: str) -> Optional[Dict[str, Any]]:
        """
        Get website content from cache (doesn't scrape if not cached)
        
        Args:
            company_domain: Company domain
        
        Returns:
            Dict with website content or None if not cached
        """
        result = self.db.table("company_websites").select("*").eq("company_domain", company_domain).eq("scraping_status", "success").execute()
        
        if result.data and len(result.data) > 0:
            cached = result.data[0]
            return {
                "domain": company_domain,
                "url": cached.get("website_url"),
                "markdown": cached.get("scraped_content"),
                "extracted_info": cached.get("extracted_info", {}),
                "scraped_at": cached.get("scraped_at")
            }
        
        return None

