from fastapi import APIRouter, HTTPException, Depends
from app.services.followup_service import FollowUpService
from app.core.database import get_db
from supabase import Client
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/schedule/{email_sent_id}")
async def schedule_followups(
    email_sent_id: UUID,
    db: Client = Depends(get_db)
):
    """
    Schedule 5-day and 10-day follow-ups for a sent email
    
    Args:
        email_sent_id: UUID of the sent email
    
    Returns:
        Dict with follow-up scheduling status
    """
    try:
        followup_service = FollowUpService()
        result = await followup_service.schedule_followups_for_sent_email(str(email_sent_id))
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to schedule follow-ups"))
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling follow-ups: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to schedule follow-ups: {str(e)}")

@router.post("/process")
async def process_due_followups(db: Client = Depends(get_db)):
    """
    Process follow-ups that are due today
    This should be called daily (can be added to scheduler)
    """
    try:
        followup_service = FollowUpService()
        result = await followup_service.process_due_followups()
        
        return result
    
    except Exception as e:
        logger.error(f"Error processing follow-ups: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process follow-ups: {str(e)}")

@router.get("/lead/{lead_id}")
async def get_lead_followups(lead_id: UUID, db: Client = Depends(get_db)):
    """Get all follow-ups for a lead"""
    try:
        followup_service = FollowUpService()
        followups = followup_service.get_followups_for_lead(str(lead_id))
        
        return {
            "lead_id": str(lead_id),
            "followups": followups,
            "count": len(followups)
        }
    
    except Exception as e:
        logger.error(f"Error getting follow-ups: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get follow-ups: {str(e)}")

@router.post("/cancel/{followup_id}")
async def cancel_followup(followup_id: UUID, db: Client = Depends(get_db)):
    """Cancel a follow-up"""
    try:
        followup_service = FollowUpService()
        result = followup_service.cancel_followup(str(followup_id))
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to cancel follow-up"))
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling follow-up: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to cancel follow-up: {str(e)}")

@router.get("/")
async def get_all_followups(
    status: str = None,
    db: Client = Depends(get_db)
):
    """Get all follow-ups, optionally filtered by status"""
    try:
        query = FollowUpService().db.table("follow_ups").select("*")
        
        if status:
            query = query.eq("status", status)
        
        query = query.order("scheduled_date")
        result = query.execute()
        
        return {
            "followups": result.data,
            "count": len(result.data)
        }
    
    except Exception as e:
        logger.error(f"Error getting follow-ups: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get follow-ups: {str(e)}")

