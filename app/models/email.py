from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class EmailQueueCreate(BaseModel):
    lead_id: UUID
    campaign_id: Optional[UUID] = None
    email_to: EmailStr
    email_subject: str
    email_body: str
    email_type: str = "initial"
    scheduled_time: datetime
    timezone: Optional[str] = None
    priority: int = 0

class EmailQueue(BaseModel):
    id: UUID
    lead_id: UUID
    campaign_id: Optional[UUID] = None
    email_to: EmailStr
    email_subject: str
    email_body: str
    email_type: str
    scheduled_time: datetime
    timezone: Optional[str] = None
    status: str
    priority: int
    retry_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EmailSentCreate(BaseModel):
    queue_id: Optional[UUID] = None
    lead_id: UUID
    campaign_id: Optional[UUID] = None
    email_to: EmailStr
    email_subject: str
    email_body: str
    email_type: str
    gmail_message_id: Optional[str] = None
    gmail_thread_id: Optional[str] = None
    is_personalized: bool = False
    company_website_used: bool = False
    timezone: Optional[str] = None

class EmailSent(BaseModel):
    id: UUID
    queue_id: Optional[UUID] = None
    lead_id: UUID
    campaign_id: Optional[UUID] = None
    email_to: EmailStr
    email_subject: str
    email_body: str
    email_type: str
    gmail_message_id: Optional[str] = None
    gmail_thread_id: Optional[str] = None
    is_personalized: bool
    company_website_used: bool
    sent_at: datetime
    timezone: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

