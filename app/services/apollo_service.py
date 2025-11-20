import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.models.apollo_search import ApolloSearchCreate
from app.models.lead import LeadCreate
import logging

logger = logging.getLogger(__name__)

class ApolloService:
    BASE_URL = "https://api.apollo.io/api/v1"
    
    def __init__(self):
        self.api_key = settings.APOLLO_API_KEY
        if not self.api_key:
            raise ValueError("APOLLO_API_KEY is required. Please add it to your .env file.")
        if self.api_key == "your_apollo_api_key_here" or self.api_key.startswith("your_"):
            raise ValueError("APOLLO_API_KEY is not set. Please add your actual Apollo API key to the .env file.")
    
    def _get_employee_size_ranges(
        self,
        employee_size_min: Optional[int] = None,
        employee_size_max: Optional[int] = None
    ) -> List[str]:
        """
        Convert employee size min/max to Apollo's range format
        Default ranges: 1-10, 11-20, 21-50, 51-100, 101-200, 201-500
        """
        # Default ranges from n8n workflow
        default_ranges = ["1,10", "11,20", "21,50", "51,100", "101,200", "201,500"]
        
        if employee_size_min is None and employee_size_max is None:
            return default_ranges
        
        # If specific range provided, use it
        if employee_size_min is not None and employee_size_max is not None:
            return [f"{employee_size_min},{employee_size_max}"]
        elif employee_size_min is not None:
            return [f"{employee_size_min},"]
        elif employee_size_max is not None:
            return [f",{employee_size_max}"]
        
        return default_ranges
    
    async def search_people(
        self,
        employee_size_min: Optional[int] = None,
        employee_size_max: Optional[int] = None,
        countries: Optional[List[str]] = None,
        sic_codes: Optional[List[str]] = None,
        c_suites: Optional[List[str]] = None,
        industry: Optional[str] = None,
        page: int = 1,
        per_page: int = 100,
        total_leads_wanted: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search for people/leads using Apollo API (matches n8n workflow)
        
        Args:
            employee_size_min: Minimum employee size
            employee_size_max: Maximum employee size
            countries: List of country codes (e.g., ["US", "IN"])
            sic_codes: List of SIC codes
            c_suites: List of C-suite titles (defaults to: CEO, COO, Director, President, Owner, Founder, Board of Directors)
            industry: Industry filter (stored for reference)
            page: Page number
            per_page: Results per page (max 100)
            total_leads_wanted: Target number of leads (for pagination calculation)
        
        Returns:
            Dict containing people data and pagination info
        """
        url = f"{self.BASE_URL}/mixed_people/search"
        
        # Default C-suite titles from n8n workflow
        if not c_suites:
            c_suites = ["CEO", "COO", "Director", "President", "Owner", "Founder", "Board of Directors"]
        
        # Build payload matching n8n workflow exactly
        # Note: Apollo requires api_key in BOTH header (x-api-key) AND body
        payload = {
            "api_key": self.api_key,  # Required in body
            "reveal_personal_emails": True,
            "email_status": ["verified", "guessed"],
            "page": page,
            "per_page": min(per_page, 100),
        }
        
        # Employee size ranges
        employee_ranges = self._get_employee_size_ranges(employee_size_min, employee_size_max)
        if employee_ranges:
            payload["organization_num_employees_ranges"] = employee_ranges
        
        # SIC codes (using organization_sic_codes as per n8n)
        if sic_codes:
            payload["organization_sic_codes"] = sic_codes
        
        # Countries (using person_locations as per n8n)
        if countries:
            payload["person_locations"] = countries
        
        # C-suite titles
        if c_suites:
            payload["person_titles"] = c_suites
        
        # Store industry for reference (not used in API but stored)
        if industry:
            payload["_industry_filter"] = industry
        
        # Headers - must include x-api-key (Apollo requires both header and body)
        request_headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "x-api-key": self.api_key  # Required in header
        }
        
        # Query params - reveal_personal_emails as query param (per n8n workflow)
        query_params = {
            "reveal_personal_emails": "true"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Making Apollo API request to: {url}")
                logger.debug(f"Payload keys: {list(payload.keys())}")
                logger.debug(f"Headers: {list(request_headers.keys())}")
                
                response = await client.post(
                    url,
                    json=payload,
                    headers=request_headers,
                    params=query_params
                )
                
                # Log response for debugging
                logger.info(f"Apollo API response status: {response.status_code}")
                
                if response.status_code == 401:
                    error_detail = response.text
                    logger.error(f"Apollo API 401 Unauthorized. Check your API key.")
                    logger.error(f"Response: {error_detail}")
                    raise Exception(f"Apollo API authentication failed (401). Please verify your APOLLO_API_KEY in .env file. Response: {error_detail}")
                
                if response.status_code == 422:
                    # Handle insufficient credits or validation errors
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", "Unknown error")
                        if "insufficient credits" in error_msg.lower():
                            logger.error("Apollo API: Insufficient credits")
                            raise Exception(f"Apollo API: Insufficient credits. Please upgrade your Apollo plan or add credits. Visit: https://app.apollo.io/#/settings/plans/upgrade")
                        else:
                            raise Exception(f"Apollo API validation error (422): {error_msg}")
                    except:
                        raise Exception(f"Apollo API error (422): {response.text}")
                
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Apollo API HTTP error: {e.response.status_code}")
            logger.error(f"Response: {e.response.text}")
            raise Exception(f"Apollo API error ({e.response.status_code}): {e.response.text}")
        except httpx.HTTPError as e:
            logger.error(f"Apollo API request error: {e}")
            raise Exception(f"Failed to fetch leads from Apollo: {str(e)}")
    
    async def get_person_details(self, person_id: str) -> Dict[str, Any]:
        """
        Get detailed person information using Apollo's match endpoint
        This reveals personal emails and additional details (matches n8n workflow)
        
        Args:
            person_id: Apollo person ID
        
        Returns:
            Dict containing detailed person data
        """
        url = f"{self.BASE_URL}/people/match"
        
        payload = {
            "id": person_id
        }
        
        headers = {
            "Cache-Control": "no-cache",
            "accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        
        query_params = {
            "reveal_personal_emails": "true"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    params=query_params
                )
                
                if response.status_code == 401:
                    logger.warning(f"Apollo person match API 401 - authentication failed for person {person_id}")
                    return {}
                
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.warning(f"Apollo person match API error ({e.response.status_code}): {e.response.text}")
            return {}  # Return empty dict if match fails, continue with original data
        except httpx.HTTPError as e:
            logger.warning(f"Apollo person match API request error: {e}")
            return {}  # Return empty dict if match fails, continue with original data
    
    def extract_email(self, person_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract email from person data (matches n8n workflow logic)
        Tries multiple locations: email, person.email, emails[0], personal_email
        """
        # Try direct email field
        if person_data.get("email"):
            return person_data.get("email")
        
        # Try person.email
        if person_data.get("person", {}).get("email"):
            return person_data.get("person", {}).get("email")
        
        # Try emails array
        if isinstance(person_data.get("emails"), list) and len(person_data.get("emails", [])) > 0:
            return person_data.get("emails")[0]
        
        # Try personal_email
        if person_data.get("personal_email"):
            return person_data.get("personal_email")
        
        return None
    
    def parse_apollo_response(
        self,
        apollo_data: Dict[str, Any],
        person_details: Optional[Dict[str, Any]] = None
    ) -> LeadCreate:
        """
        Parse Apollo API response into LeadCreate object (matches n8n workflow)
        
        Args:
            apollo_data: Raw person data from Apollo search
            person_details: Optional detailed person data from match endpoint
        
        Returns:
            LeadCreate object
        """
        # Use detailed data if available, otherwise use original
        person = person_details.get("person", apollo_data) if person_details else apollo_data
        
        # Extract organization data
        organization = person.get("organization", {})
        
        # Extract email using the extraction logic
        email = self.extract_email(person)
        if person_details:
            # Try to get email from person_details too
            email = email or self.extract_email(person_details)
        
        # Extract name
        name = person.get("name", "")
        if not name:
            first_name = person.get("first_name", "")
            last_name = person.get("last_name", "")
            name = f"{first_name} {last_name}".strip()
        
        lead = LeadCreate(
            apollo_id=str(person.get("id", "")),
            first_name=person.get("first_name"),
            last_name=person.get("last_name"),
            email=email,
            title=person.get("title"),
            company_name=organization.get("name"),
            company_domain=organization.get("primary_domain"),
            company_website=organization.get("website_url"),
            company_linkedin_url=organization.get("linkedin_url"),
            company_blog_url=organization.get("blog_url"),
            company_angellist_url=organization.get("angellist_url"),
            company_employee_size=organization.get("estimated_num_employees"),
            company_country=self._extract_country(organization),
            company_industry=organization.get("industry"),
            company_sic_code=organization.get("sic_code"),
            linkedin_url=person.get("linkedin_url"),
            phone=self._extract_phone(person, organization),
            location=person.get("city") or organization.get("city"),
            formatted_address=person.get("formatted_address"),
            is_c_suite=self._is_c_suite(person.get("title", "")),
            apollo_data=person,
            status="new"
        )
        
        return lead
    
    def _extract_country(self, organization: Dict[str, Any]) -> Optional[str]:
        """Extract country from organization data"""
        # Try various locations for country
        if organization.get("country"):
            return organization.get("country")
        if organization.get("primary_location", {}).get("country"):
            return organization.get("primary_location", {}).get("country")
        return None
    
    def _extract_phone(self, person: Dict[str, Any], organization: Dict[str, Any]) -> Optional[str]:
        """Extract phone number from person or organization"""
        # Try person phone
        if person.get("phone_numbers") and len(person.get("phone_numbers", [])) > 0:
            return person.get("phone_numbers")[0].get("raw_number")
        
        # Try organization phone
        if organization.get("phone_numbers") and len(organization.get("phone_numbers", [])) > 0:
            return organization.get("phone_numbers")[0].get("raw_number")
        
        # Try organization.phone (from n8n workflow)
        if organization.get("phone"):
            return organization.get("phone")
        
        return None
    
    def _is_c_suite(self, title: str) -> bool:
        """Check if title is C-suite (matches n8n workflow titles)"""
        if not title:
            return False
        title_lower = title.lower()
        c_suite_titles = [
            "ceo", "coo", "director", "president", "owner", 
            "founder", "board of directors", "cfo", "cto", "cmo"
        ]
        return any(c_title in title_lower for c_title in c_suite_titles)

