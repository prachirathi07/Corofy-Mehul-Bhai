from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.core.database import get_db
from supabase import Client
from uuid import UUID

router = APIRouter()

@router.get("/")
async def get_campaigns(db: Client = Depends(get_db)):
    """Get all campaigns"""
    result = db.table("email_campaigns").select("*").order("created_at", desc=True).execute()
    return result.data

@router.get("/{campaign_id}")
async def get_campaign(campaign_id: UUID, db: Client = Depends(get_db)):
    """Get a specific campaign"""
    result = db.table("email_campaigns").select("*").eq("id", campaign_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return result.data[0]

