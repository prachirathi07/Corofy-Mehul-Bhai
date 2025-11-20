from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class LeadBase(BaseModel):
    apollo_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    company_domain: Optional[str] = None
    company_website: Optional[str] = None
    company_linkedin_url: Optional[str] = None
    company_blog_url: Optional[str] = None  # From n8n workflow
    company_angellist_url: Optional[str] = None  # From n8n workflow
    company_employee_size: Optional[int] = None
    company_country: Optional[str] = None
    company_industry: Optional[str] = None
    company_sic_code: Optional[str] = None
    linkedin_url: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    formatted_address: Optional[str] = None  # From n8n workflow
    is_c_suite: bool = False
    status: str = "new"

class LeadCreate(LeadBase):
    apollo_search_id: Optional[UUID] = None
    apollo_data: Optional[Dict[str, Any]] = None

class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    company_domain: Optional[str] = None
    company_website: Optional[str] = None
    status: Optional[str] = None
    apollo_data: Optional[Dict[str, Any]] = None

class Lead(LeadBase):
    id: UUID
    apollo_search_id: Optional[UUID] = None
    apollo_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

