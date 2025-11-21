import httpx
import asyncio
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
        total_leads_wanted: int = 625
    ) -> List[LeadCreate]:
        """
        Search for people/leads using Apollo API (matches n8n workflow exactly)
        Implements: Search with pagination → Match each person → Parse → Return leads
        
        Args:
            employee_size_min: Minimum employee size
            employee_size_max: Maximum employee size
            countries: List of country codes (e.g., ["US", "IN"])
            sic_codes: List of SIC codes
            c_suites: List of C-suite titles (defaults to: CEO, COO, Director, President, Owner, Founder, Board of Directors)
            industry: Industry filter (stored for reference)
            total_leads_wanted: Target number of leads (default: 625, matches n8n)
        
        Returns:
            List of LeadCreate objects
        """
        # Default C-suite titles from n8n workflow
        if not c_suites:
            c_suites = ["CEO", "COO", "Director", "President", "Owner", "Founder", "Board of Directors"]
        
        # Calculate pagination (matches n8n workflow: 8 pages for 625 leads)
        leads_per_page = 100  # Apollo max
        total_pages = (total_leads_wanted + leads_per_page - 1) // leads_per_page  # Ceiling division
        
        logger.info(f"Apollo: Fetching {total_leads_wanted} leads across {total_pages} pages")
        
        all_people = []
        
        # Step 1: Search with pagination (matches n8n Code5 → HTTP Request4)
        for page in range(1, total_pages + 1):
            try:
                logger.info(f"Apollo: Fetching page {page}/{total_pages}")
                
                # Build payload matching n8n workflow exactly
                payload = {
                    "api_key": self.api_key,
                    "organization_sic_codes": sic_codes or [],
                    "person_locations": countries or [],
                    "person_titles": c_suites,
                    "organization_num_employees_ranges": self._get_employee_size_ranges(employee_size_min, employee_size_max),
                    "reveal_personal_emails": True,
                    "email_status": ["verified", "guessed"],
                    "page": page,
                    "per_page": leads_per_page,
                    "_industry_filter": industry or ""
                }
                
                # Headers matching n8n workflow
                headers = {
                    "Cache-Control": "no-cache",
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json"
                }
                
                # Query params
                query_params = {
                    "reveal_personal_emails": "true"
                }
                
                url = f"{self.BASE_URL}/mixed_people/search"
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        url,
                        json=payload,
                        headers=headers,
                        params=query_params
                    )
                    
                    if response.status_code == 401:
                        raise Exception(f"Apollo API authentication failed (401). Check your API key.")
                    
                    if response.status_code == 422:
                        error_data = response.json()
                        error_msg = error_data.get("error", "Unknown error")
                        if "insufficient credits" in error_msg.lower():
                            raise Exception(f"Apollo API: Insufficient credits. Please upgrade your plan.")
                        raise Exception(f"Apollo API validation error (422): {error_msg}")
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    # Extract people array (matches n8n Split Out2)
                    people = data.get("people", [])
                    logger.info(f"Apollo: Page {page} returned {len(people)} people")
                    all_people.extend(people)
                    
                    # Stop if we have enough leads
                    if len(all_people) >= total_leads_wanted:
                        all_people = all_people[:total_leads_wanted]
                        break
                        
            except Exception as e:
                logger.error(f"Apollo: Error fetching page {page}: {e}")
                # Continue with other pages
                continue
        
        logger.info(f"Apollo: Total {len(all_people)} people found from search")
        
        # Step 2: For each person, get full details via match endpoint (matches n8n HTTP Request5)
        all_leads = []
        for idx, person in enumerate(all_people):
            try:
                person_id = person.get("id")
                if not person_id:
                    logger.warning(f"Apollo: Person {idx} has no ID, skipping")
                    continue
                
                # Small delay to avoid rate limiting (0.1s between match calls)
                if idx > 0:
                    await asyncio.sleep(0.1)
                
                # Call match endpoint to get full details (matches n8n HTTP Request5)
                person_details = await self.get_person_details(str(person_id))
                
                # Extract email (matches n8n Code node)
                email = self.extract_email(person)
                if not email and person_details:
                    email = self.extract_email(person_details)
                
                # Parse into LeadCreate (matches n8n Edit Fields2)
                lead = self.parse_apollo_response(person, person_details)
                
                # Override email if we found it
                if email:
                    lead.email = email
                
                all_leads.append(lead)
                
                # Log progress every 50 leads
                if (idx + 1) % 50 == 0:
                    logger.info(f"Apollo: Processed {idx + 1}/{len(all_people)} people")
                    
            except Exception as e:
                logger.warning(f"Apollo: Error processing person {idx}: {e}")
                # Try to create lead from original data without match
                try:
                    lead = self.parse_apollo_response(person, None)
                    all_leads.append(lead)
                except:
                    logger.error(f"Apollo: Failed to parse person {idx}, skipping")
                    continue
        
        logger.info(f"Apollo: Successfully parsed {len(all_leads)} leads")
        return all_leads
    
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
        Parse Apollo API response into LeadCreate object (matches n8n Edit Fields2 exactly)
        
        Args:
            apollo_data: Raw person data from Apollo search
            person_details: Optional detailed person data from match endpoint
        
        Returns:
            LeadCreate object
        """
        # Use detailed data if available, otherwise use original (matches n8n flow)
        if person_details and person_details.get("person"):
            person = person_details.get("person")
        else:
            person = apollo_data
        
        # Extract organization data
        organization = person.get("organization", {})
        
        # Extract fields matching n8n Edit Fields2 node exactly
        name = person.get("name", "")
        linkedin_url = person.get("linkedin_url", "")
        title = person.get("title", "")
        formatted_address = person.get("formatted_address", "")
        
        # Extract organization fields
        company_name = organization.get("name", "")
        company_website = organization.get("website_url", "")
        company_linkedin = organization.get("linkedin_url", "")
        company_blog = organization.get("blog_url", "")
        company_angellist = organization.get("angellist_url", "")
        company_phone = organization.get("phone", "")
        
        # Extract email (already extracted in search_people, but keep for safety)
        email = self.extract_email(person)
        if not email and person_details:
            email = self.extract_email(person_details)
        
        # Split name into first/last
        name_parts = name.split(" ", 1) if name else ["", ""]
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # If no name, try first_name/last_name fields
        if not first_name:
            first_name = person.get("first_name", "")
        if not last_name:
            last_name = person.get("last_name", "")
        
        lead = LeadCreate(
            apollo_id=str(person.get("id", "")),
            first_name=first_name,
            last_name=last_name,
            email=email,
            title=title,
            company_name=company_name,
            company_domain=organization.get("primary_domain") or organization.get("website_url", "").replace("https://", "").replace("http://", "").split("/")[0],
            company_website=company_website,
            company_linkedin_url=company_linkedin,
            company_blog_url=company_blog,
            company_angellist_url=company_angellist,
            company_employee_size=organization.get("estimated_num_employees"),
            company_country=self._extract_country(organization),
            company_industry=organization.get("industry") or apollo_data.get("_industry_filter"),
            company_sic_code=organization.get("sic_code"),
            linkedin_url=linkedin_url,
            phone=company_phone or self._extract_phone(person, organization),
            location=person.get("city") or organization.get("city"),
            formatted_address=formatted_address,
            is_c_suite=self._is_c_suite(title),
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

