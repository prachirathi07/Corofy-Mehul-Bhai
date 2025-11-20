from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ApolloSearchBase(BaseModel):
    employee_size_min: Optional[int] = None
    employee_size_max: Optional[int] = None
    country: Optional[str] = None
    sic_codes: Optional[List[str]] = None
    c_suites: Optional[List[str]] = None

class ApolloSearchCreate(ApolloSearchBase):
    status: str = "pending"

class ApolloSearchUpdate(BaseModel):
    status: Optional[str] = None
    total_leads_found: Optional[int] = None
    completed_at: Optional[datetime] = None

class ApolloSearch(ApolloSearchBase):
    id: UUID
    status: str
    total_leads_found: int = 0
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

