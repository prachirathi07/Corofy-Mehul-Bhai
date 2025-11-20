"""
Factory for creating lead scraper services (Apollo or Apify)
"""
from typing import Optional, Union
from app.services.apollo_service import ApolloService
from app.services.apify_service import ApifyService
import logging

logger = logging.getLogger(__name__)

class LeadScraperFactory:
    """
    Factory to create and manage lead scraper services
    """
    
    @staticmethod
    def create_scraper(source: str = "apify") -> Union[ApolloService, ApifyService]:
        """
        Create a lead scraper service based on source
        
        Args:
            source: "apollo" or "apify"
        
        Returns:
            ApolloService or ApifyService instance
        """
        source = source.lower()
        
        if source == "apollo":
            try:
                return ApolloService()
            except ValueError as e:
                logger.error(f"Failed to create ApolloService: {e}")
                raise
        
        elif source == "apify":
            try:
                logger.info("Attempting to create ApifyService...")
                service = ApifyService()
                logger.info("ApifyService created successfully")
                return service
            except ValueError as e:
                logger.error(f"Failed to create ApifyService: {e}")
                raise ValueError(f"Cannot use Apify: {e}. Please add APIFY_API_TOKEN and APIFY_ACTOR_ID to .env file.")
        
        else:
            raise ValueError(f"Unknown scraper source: {source}. Use 'apollo' or 'apify'")
    
    @staticmethod
    def get_available_sources() -> list:
        """Get list of available scraper sources"""
        sources = []
        
        try:
            ApolloService()
            sources.append("apollo")
        except:
            pass
        
        try:
            ApifyService()
            sources.append("apify")
        except:
            pass
        
        return sources

