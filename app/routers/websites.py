from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.services.website_service import WebsiteService
from app.core.database import get_db
from supabase import Client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/scrape")
async def scrape_website(
    company_domain: str,
    company_website: Optional[str] = None,
    db: Client = Depends(get_db)
):
    """
    Scrape a company website using Firecrawl
    
    Args:
        company_domain: Company domain (e.g., "example.com" or "https://example.com")
        company_website: Full website URL (optional, will be constructed from domain if not provided)
    
    Returns:
        Dict containing scraped content and status
    """
    try:
        # Extract clean domain from company_domain (handles both "example.com" and "https://example.com")
        from urllib.parse import urlparse
        if company_domain.startswith(("http://", "https://")):
            parsed = urlparse(company_domain)
            clean_domain = parsed.netloc or company_domain
            # Use the full URL as company_website if not provided
            if not company_website:
                company_website = company_domain
        else:
            clean_domain = company_domain.replace("www.", "")
        
        # Remove www. prefix from domain
        if clean_domain.startswith("www."):
            clean_domain = clean_domain[4:]
        
        website_service = WebsiteService(db)
        result = await website_service.scrape_company_website(
            company_domain=clean_domain,
            company_website=company_website
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error scraping website: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to scrape website: {str(e)}")

@router.get("/{company_domain}")
async def get_website_content(
    company_domain: str,
    db: Client = Depends(get_db)
):
    """
    Get cached website content for a company domain
    
    Args:
        company_domain: Company domain
    
    Returns:
        Dict with website content or 404 if not found
    """
    try:
        website_service = WebsiteService(db)
        content = await website_service.get_website_content(company_domain)
        
        if not content:
            raise HTTPException(status_code=404, detail=f"Website content not found for {company_domain}")
        
        return content
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting website content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get website content: {str(e)}")

@router.get("/")
async def list_scraped_websites(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Client = Depends(get_db)
):
    """
    List all scraped websites with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Filter by scraping status (pending, success, failed)
    
    Returns:
        List of scraped website records
    """
    try:
        query = db.table("company_websites").select("*")
        
        if status:
            query = query.eq("scraping_status", status)
        
        query = query.order("scraped_at", desc=True).range(skip, skip + limit - 1)
        result = query.execute()
        
        return result.data
    
    except Exception as e:
        logger.error(f"Error listing websites: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list websites: {str(e)}")

