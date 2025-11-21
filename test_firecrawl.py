"""
Test script to verify Firecrawl scraping service
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
import logging

# Fix for Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.firecrawl_service import FirecrawlService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    print("\n" + "="*80)
    print("🔥 FIRECRAWL TEST")
    print("="*80)
    
    load_dotenv()
    
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("\n❌ ERROR: FIRECRAWL_API_KEY not set in .env file")
        return
        
    print(f"\n✅ API Key found: {api_key[:10]}...")
    
    service = FirecrawlService()
    url = "https://example.com"
    
    print(f"\n🌐 Scraping {url}...")
    
    result = await service.scrape_website(url)
    
    if result.get("success"):
        print("\n✅ Scrape Successful!")
        print(f"   URL: {result.get('url')}")
        print(f"   Content Length: {len(result.get('markdown', ''))}")
        print(f"   Title: {result.get('title')}")
        print(f"   Description: {result.get('description')}")
        print("\n📄 Content Preview:")
        print("-" * 40)
        print(result.get("markdown", "")[:500])
        print("-" * 40)
    else:
        print(f"\n❌ Scrape Failed: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
