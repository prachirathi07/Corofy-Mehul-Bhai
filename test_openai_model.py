import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.openai_service import OpenAIService

async def test_openai_with_new_model():
    print("🧪 Testing OpenAI Service with new model...")
    print("=" * 60)
    
    try:
        # Initialize service
        service = OpenAIService()
        print(f"✅ OpenAI Service initialized")
        print(f"📋 Model: {service.model}")
        print()
        
        # Test email generation
        print("🤖 Generating test email...")
        result = await service.generate_personalized_email(
            lead_name="John Doe",
            lead_title="CEO",
            company_name="AgroCorp",
            company_website_content="AgroCorp is a leading agricultural company specializing in crop protection and fertilizers.",
            company_industry="Agriculture",
            email_type="initial"
        )
        
        if result.get("success"):
            print("✅ Email generation SUCCESSFUL!")
            print()
            print(f"📧 Subject: {result.get('subject')}")
            print(f"🏭 Industry: {result.get('industry')}")
            print(f"📝 Body preview: {result.get('body')[:200]}...")
            print()
            print("=" * 60)
            print("✅ ALL TESTS PASSED! OpenAI is working correctly.")
        else:
            print("❌ Email generation FAILED")
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Test FAILED with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_openai_with_new_model())
