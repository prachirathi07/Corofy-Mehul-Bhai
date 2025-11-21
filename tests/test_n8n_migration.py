import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_personalization_service import EmailPersonalizationService
from app.core.email_data import EMAIL_TEMPLATES

async def test_with_website_content():
    """Test that industry-specific templates are used when website content is available"""
    print("🧪 Test 1: WITH Website Content (should use Agrochemical template)...")

    # Mock Database
    mock_db = MagicMock()
    
    # Mock Lead Data
    mock_lead = {
        "id": "test-lead-id",
        "first_name": "John",
        "last_name": "Doe",
        "company_name": "AgroCorp",
        "company_domain": "agrocorp.com",
        "company_website": "https://agrocorp.com",
        "title": "Manager"
    }
    
    # Setup DB mock to return this lead
    mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_lead]
    
    # Mock EmailPersonalizationService
    service = EmailPersonalizationService(mock_db)
    
    # Mock WebsiteService to return REAL content (simulating successful scrape)
    service.website_service.get_website_content = AsyncMock(return_value={
        "markdown": "AgroCorp is a leading agricultural company specializing in crop protection..."
    })

    # MOCK OpenAI Service
    mock_openai_response = {
        "success": True,
        "industry": "Agrochemical",
        "subject": "Boost your crops with Corofy",
        "body": "We have great Calcium Alkylbenzene Sulfonate and other agro products.",
        "is_personalized": True
    }
    service.openai_service.generate_personalized_email = AsyncMock(return_value=mock_openai_response)

    # Run the generation
    result = await service.generate_email_for_lead("test-lead-id", force_regenerate=True)

    # Verify Result
    if result["success"]:
        print("   ✅ Generation Successful")
        
        body = result["body"]
        
        # Check for industry-specific template
        if "Agro Chemicals we offer include" in body:
            print("   ✅ Correctly selected Agrochemical Template")
        else:
            print("   ❌ Failed to select Agrochemical Template")
            
        if "Calcium Alkylbenzene Sulfonate" in body:
            print("   ✅ Product list is present")
        else:
            print("   ❌ Product list missing")
            
        if "Mehul Parmar" in body:
            print("   ✅ Signature is present")
        else:
            print("   ❌ Signature missing")

    else:
        print(f"   ❌ Generation Failed: {result.get('error')}")

async def test_without_website_content():
    """Test that DEFAULT template is used when NO website content is available"""
    print("\n🧪 Test 2: WITHOUT Website Content (should use DEFAULT template)...")

    # Mock Database
    mock_db = MagicMock()
    
    # Mock Lead Data
    mock_lead = {
        "id": "test-lead-id-2",
        "first_name": "Jane",
        "last_name": "Smith",
        "company_name": "TechCorp",
        "company_domain": "techcorp.com",
        "company_website": "https://techcorp.com",
        "title": "CEO"
    }
    
    # Setup DB mock to return this lead
    mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_lead]
    
    # Mock EmailPersonalizationService
    service = EmailPersonalizationService(mock_db)
    
    # Mock WebsiteService to return NO content (simulating failed scrape)
    service.website_service.get_website_content = AsyncMock(return_value=None)
    service.website_service.scrape_company_website = AsyncMock(return_value={"success": False})

    # MOCK OpenAI Service (even if AI says "Oil & Gas", we should ignore it)
    mock_openai_response = {
        "success": True,
        "industry": "Oil & Gas",  # AI thinks it's Oil & Gas
        "subject": "Partnership opportunity",
        "body": "We noticed your company and would love to collaborate.",
        "is_personalized": False
    }
    service.openai_service.generate_personalized_email = AsyncMock(return_value=mock_openai_response)

    # Run the generation
    result = await service.generate_email_for_lead("test-lead-id-2", force_regenerate=True)

    # Verify Result
    if result["success"]:
        print("   ✅ Generation Successful")
        
        body = result["body"]
        
        # Should NOT have industry-specific content
        if "Oil & Gas Chemicals we offer include" not in body:
            print("   ✅ Correctly avoided Oil & Gas template")
        else:
            print("   ❌ Incorrectly used Oil & Gas template")
            
        # Should have generic signature (from DEFAULT_TEMPLATE)
        if "Mehul Parmar" in body:
            print("   ✅ Default signature is present")
        else:
            print("   ❌ Default signature missing")
            
        # Check that industry was forced to "Other"
        if result.get("industry") == "Other":
            print("   ✅ Industry correctly set to 'Other'")
        else:
            print(f"   ❌ Industry incorrectly set to '{result.get('industry')}'")

    else:
        print(f"   ❌ Generation Failed: {result.get('error')}")

async def main():
    print("=" * 80)
    print("Testing n8n Migration Logic: Industry-Specific vs Default Templates")
    print("=" * 80)
    
    await test_with_website_content()
    await test_without_website_content()
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
