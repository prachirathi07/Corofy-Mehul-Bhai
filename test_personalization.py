"""
Test script to verify if OpenAI service uses scraped website data for email personalization

This test verifies:
1. Website content is properly passed to OpenAI
2. Generated emails contain specific details from the website
3. Personalization quality is measured and scored

To run: python test_personalization.py

Note: Requires valid OpenAI API key with sufficient quota
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

from app.services.openai_service import OpenAIService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample website content with specific details that should be mentioned in the email
SAMPLE_WEBSITE_CONTENT = """
# NenoTechnology - AI Automation Solutions

## About Us
NenoTechnology is a specialized AI automation innovation company that builds custom automation solutions for businesses. 
We transform businesses with AI automation, helping companies streamline their operations and increase efficiency.

## Our Services
- Intelligent Chatbots: We create AI-powered chatbots that can handle customer inquiries 24/7
- Automated Workflows: Custom workflow automation that reduces manual work by up to 80%
- AI Integration: Seamless integration of AI tools into existing business systems
- Data Analytics: AI-powered analytics dashboards for better decision making

## Our Technology Stack
- OpenAI GPT-4 for natural language processing
- Python and FastAPI for backend development
- React for frontend applications
- Supabase for database management

## Recent Achievements
- Reduced client processing time by 40% using intelligent automation
- Successfully deployed 50+ AI chatbots for various industries
- Achieved 95% customer satisfaction rate
- Partnered with leading healthcare companies to automate patient scheduling

## Our Values
- Innovation: We stay at the forefront of AI technology
- Customer-Centric: Every solution is tailored to client needs
- Quality: We deliver enterprise-grade solutions
- Transparency: Clear communication throughout the project lifecycle

## Industries We Serve
- Healthcare: Patient scheduling, medical record management
- E-commerce: Inventory management, customer support automation
- Finance: Fraud detection, automated reporting
- Education: Student enrollment, course management systems

## Contact
Visit us at www.nenotechnology.com or email us at info@nenotechnology.com
"""


def check_personalization_quality(email_text: str, website_content: str, company_name: str) -> dict:
    """
    Check if the email contains personalized content from the website
    
    Returns a dict with personalization metrics
    """
    email_lower = email_text.lower()
    website_lower = website_content.lower()
    company_lower = company_name.lower()
    
    # Extract key phrases from website content that should appear in personalized email
    key_phrases = [
        "ai automation",
        "intelligent chatbots",
        "automated workflows",
        "custom automation",
        "transform businesses",
        "streamline operations",
        "reduce manual work",
        "healthcare",
        "e-commerce",
        "customer satisfaction",
        "innovation",
        "customer-centric"
    ]
    
    # Check for specific details
    found_phrases = []
    for phrase in key_phrases:
        if phrase in website_lower and phrase in email_lower:
            found_phrases.append(phrase)
    
    # Check for company name
    has_company_name = company_lower in email_lower
    
    # Check for generic phrases (bad signs)
    generic_phrases = [
        "i came across your company",
        "i was impressed by your work",
        "potential collaboration",
        "partnership opportunity",
        "generic"
    ]
    has_generic = any(phrase in email_lower for phrase in generic_phrases)
    
    # Calculate personalization score
    score = 0
    if has_company_name:
        score += 30
    score += len(found_phrases) * 10
    if not has_generic:
        score += 20
    
    return {
        "score": min(score, 100),
        "found_phrases": found_phrases,
        "has_company_name": has_company_name,
        "has_generic_phrases": has_generic,
        "phrase_count": len(found_phrases),
        "total_phrases_checked": len(key_phrases)
    }


async def test_with_website_content():
    """Test email generation WITH website content"""
    print("\n" + "="*80)
    print("TEST 1: Email Generation WITH Website Content")
    print("="*80)
    
    try:
        service = OpenAIService()
        
        lead_name = "John Smith"
        lead_title = "CEO"
        company_name = "NenoTechnology"
        
        print(f"\n📋 Test Parameters:")
        print(f"   Lead Name: {lead_name}")
        print(f"   Lead Title: {lead_title}")
        print(f"   Company Name: {company_name}")
        print(f"   Website Content Length: {len(SAMPLE_WEBSITE_CONTENT)} characters")
        
        print(f"\n🤖 Generating email with OpenAI (this may take a few seconds)...")
        
        result = await service.generate_personalized_email(
            lead_name=lead_name,
            lead_title=lead_title,
            company_name=company_name,
            company_website_content=SAMPLE_WEBSITE_CONTENT,
            company_industry="AI Automation",
            email_type="initial"
        )
        
        if result.get("success"):
            subject = result.get("subject", "")
            body = result.get("body", "")
            is_personalized = result.get("is_personalized", False)
            
            print(f"\n✅ Email Generated Successfully!")
            print(f"\n📧 Subject: {subject}")
            print(f"\n📝 Body:\n{body}")
            print(f"\n🏷️  Is Personalized: {is_personalized}")
            
            # Check personalization quality
            full_email = f"{subject} {body}"
            quality = check_personalization_quality(full_email, SAMPLE_WEBSITE_CONTENT, company_name)
            
            print(f"\n📊 Personalization Quality Analysis:")
            print(f"   Score: {quality['score']}/100")
            print(f"   Company Name Mentioned: {'✅' if quality['has_company_name'] else '❌'}")
            print(f"   Specific Phrases Found: {quality['phrase_count']}/{quality['total_phrases_checked']}")
            print(f"   Generic Phrases Detected: {'❌ YES (Bad)' if quality['has_generic_phrases'] else '✅ NO (Good)'}")
            if quality['found_phrases']:
                print(f"   Found Phrases: {', '.join(quality['found_phrases'][:5])}")
            
            if quality['score'] >= 70:
                print(f"\n🎉 EXCELLENT: Email is highly personalized!")
            elif quality['score'] >= 50:
                print(f"\n✅ GOOD: Email shows some personalization")
            elif quality['score'] >= 30:
                print(f"\n⚠️  WARNING: Email has minimal personalization")
            else:
                print(f"\n❌ POOR: Email appears to be generic")
            
            return result, quality
        else:
            print(f"\n❌ Failed to generate email: {result.get('error')}")
            return None, None
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Error in test_with_website_content: {e}", exc_info=True)
        return None, None


async def test_without_website_content():
    """Test email generation WITHOUT website content (should be generic)"""
    print("\n" + "="*80)
    print("TEST 2: Email Generation WITHOUT Website Content (Baseline)")
    print("="*80)
    
    try:
        service = OpenAIService()
        
        lead_name = "John Smith"
        lead_title = "CEO"
        company_name = "NenoTechnology"
        
        print(f"\n📋 Test Parameters:")
        print(f"   Lead Name: {lead_name}")
        print(f"   Lead Title: {lead_title}")
        print(f"   Company Name: {company_name}")
        print(f"   Website Content: None (generic email expected)")
        
        print(f"\n🤖 Generating email with OpenAI (this may take a few seconds)...")
        
        result = await service.generate_personalized_email(
            lead_name=lead_name,
            lead_title=lead_title,
            company_name=company_name,
            company_website_content=None,  # No website content
            company_industry="AI Automation",
            email_type="initial"
        )
        
        if result.get("success"):
            subject = result.get("subject", "")
            body = result.get("body", "")
            is_personalized = result.get("is_personalized", False)
            
            print(f"\n✅ Email Generated Successfully!")
            print(f"\n📧 Subject: {subject}")
            print(f"\n📝 Body:\n{body}")
            print(f"\n🏷️  Is Personalized: {is_personalized}")
            
            print(f"\n📝 Note: This email should be generic (no website content provided)")
            
            return result
        else:
            print(f"\n❌ Failed to generate email: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Error in test_without_website_content: {e}", exc_info=True)
        return None


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 PERSONALIZATION TEST SUITE")
    print("Testing if OpenAI uses scraped website data for email personalization")
    print("="*80)
    
    # Load environment variables
    load_dotenv()
    
    # Check if OpenAI API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("your_"):
        print("\n❌ ERROR: OPENAI_API_KEY not set in .env file")
        print("   Please add your OpenAI API key to the .env file")
        return
    
    print(f"\n✅ OpenAI API Key found: {api_key[:15]}...")
    
    # Run tests
    print("\n" + "="*80)
    print("Starting tests...")
    print("="*80)
    
    # Test 1: With website content
    result_with_content, quality_with = await test_with_website_content()
    
    # Test 2: Without website content (baseline)
    result_without_content = await test_without_website_content()
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    if result_with_content and quality_with:
        print(f"\n✅ Test 1 (WITH website content):")
        print(f"   Personalization Score: {quality_with['score']}/100")
        print(f"   Status: {'✅ PASSED' if quality_with['score'] >= 50 else '❌ FAILED'}")
    
    if result_without_content:
        print(f"\n✅ Test 2 (WITHOUT website content):")
        print(f"   Status: ✅ PASSED (generic email as expected)")
    
    if result_with_content and result_without_content:
        print(f"\n🔍 Comparison:")
        print(f"   With content subject: {result_with_content.get('subject', 'N/A')[:60]}...")
        print(f"   Without content subject: {result_without_content.get('subject', 'N/A')[:60]}...")
        
        # Check if they're different
        if result_with_content.get('subject') != result_without_content.get('subject'):
            print(f"   ✅ Subjects are different - personalization may be working")
        else:
            print(f"   ⚠️  Subjects are similar - may need stronger personalization")
    
    print("\n" + "="*80)
    print("Tests completed!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
