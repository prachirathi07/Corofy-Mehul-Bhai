"""
Factory for creating lead scraper services (Apollo only)
"""
from typing import Optional
from app.services.apollo_service import ApolloService
import logging

logger = logging.getLogger(__name__)

class LeadScraperFactory:
    """
    Factory to create and manage lead scraper services
    """
    
    @staticmethod
    def create_scraper(source: str = "apollo") -> ApolloService:
        """
        Create a lead scraper service based on source
        
        Args:
            source: "apollo" (only supported source)
        
        Returns:
            ApolloService instance
        """
        source = source.lower()
        
        if source == "apollo":
            try:
                return ApolloService()
            except ValueError as e:
                logger.error(f"Failed to create ApolloService: {e}")
                raise
        else:
            raise ValueError(f"Unknown scraper source: {source}. Only 'apollo' is supported.")
    
    @staticmethod
    def get_available_sources() -> list:
        """Get list of available scraper sources"""
        sources = []
        
        try:
            ApolloService()
            sources.append("apollo")
        except:
            pass
        
        return sources

