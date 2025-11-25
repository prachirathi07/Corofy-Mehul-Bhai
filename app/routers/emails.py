from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime
from app.services.email_personalization_service import EmailPersonalizationService
from app.services.email_sending_service import EmailSendingService
from app.core.database import get_db
from supabase import Client
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate/{lead_id}")
async def generate_email(
    lead_id: UUID,
    email_type: Optional[str] = "initial",
    force_regenerate: Optional[bool] = False,
    db: Client = Depends(get_db)
):
    """
    Generate a personalized email for a lead
    
    Args:
        lead_id: Lead UUID
        email_type: Type of email (initial, followup_5day, followup_10day)
        force_regenerate: Force regeneration even if email exists
    
    Returns:
        Dict with email subject, body, and metadata
    """
    try:
        email_service = EmailPersonalizationService(db)
        result = await email_service.generate_email_for_lead(
            lead_id=str(lead_id),
            email_type=email_type,
            force_regenerate=force_regenerate
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to generate email"))
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating email: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate email: {str(e)}")

@router.get("/queue")
async def get_email_queue(db: Client = Depends(get_db)):
    """Get pending emails in queue (using scheduled_emails view)"""
    try:
        # Use the view created in migration
        result = db.table("scheduled_emails").select("*").order("scheduled_time").execute()
        return result.data
    except Exception as e:
        # Fallback to direct query if view doesn't exist
        logger.warning(f"View scheduled_emails might not exist, falling back to scraped_data: {e}")
        result = db.table("scraped_data").select("*").eq("mail_status", "scheduled").order("scheduled_time").execute()
        return result.data

@router.get("/sent")
async def get_sent_emails(
    skip: int = 0,
    limit: int = 50,
    lead_id: Optional[UUID] = None,
    db: Client = Depends(get_db)
):
    """Get all sent emails (using sent_emails_view)"""
    try:
        query = db.table("sent_emails_view").select("*")
        
        if lead_id:
            query = query.eq("lead_id", str(lead_id))
        
        query = query.order("sent_at", desc=True).range(skip, skip + limit - 1)
        result = query.execute()
        
        return result.data
    except Exception as e:
        # Fallback
        logger.warning(f"View sent_emails_view might not exist, falling back to scraped_data: {e}")
        query = db.table("scraped_data").select("*").in_("mail_status", ["email_sent", "sent", "reply_received", "2nd followup sent"])
        if lead_id:
            query = query.eq("id", str(lead_id))
        query = query.order("sent_at", desc=True).range(skip, skip + limit - 1)
        result = query.execute()
        return result.data

@router.get("/sent/{email_id}")
async def get_sent_email(email_id: UUID, db: Client = Depends(get_db)):
    """Get a specific sent email (by lead_id since 1:1 mapping now)"""
    # Note: email_id is interpreted as lead_id in the simplified schema
    try:
        result = db.table("sent_emails_view").select("*").eq("lead_id", str(email_id)).execute()
        
        if not result.data:
            # Try scraped_data directly
            result = db.table("scraped_data").select("*").eq("id", str(email_id)).execute()
            if not result.data:
                raise HTTPException(status_code=404, detail="Email/Lead not found")
        
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send/{lead_id}")
async def send_email_to_lead(
    lead_id: UUID,
    email_type: str = "initial",
    schedule_time: Optional[str] = None,
    db: Client = Depends(get_db)
):
    """
    Send an email to a lead
    
    Args:
        lead_id: Lead UUID
        email_type: Type of email (initial, followup_5day, followup_10day)
        schedule_time: Optional ISO datetime string to schedule the email (if None, sends immediately if in business hours)
    
    Returns:
        Dict with send status
    """
    try:
        email_sending_service = EmailSendingService(db)
        
        # Parse schedule_time if provided
        scheduled_datetime = None
        if schedule_time:
            try:
                scheduled_datetime = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid schedule_time format: {str(e)}")
        
        result = await email_sending_service.send_email_to_lead(
            lead_id=str(lead_id),
            email_type=email_type,
            schedule_time=scheduled_datetime
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to send email"))
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@router.post("/queue/process")
async def process_email_queue(db: Client = Depends(get_db)):
    """
    Process pending emails in the queue that are ready to send
    This endpoint should be called periodically (every 2 hours) to send scheduled emails
    """
    try:
        email_sending_service = EmailSendingService(db)
        result = await email_sending_service.process_email_queue()
        
        return result
    
    except Exception as e:
        logger.error(f"Error processing email queue: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process email queue: {str(e)}")

@router.post("/reset-sent-status")
async def reset_sent_emails_status(db: Client = Depends(get_db)):
    """
    Reset all emails with status 'email_sent' or 'sent' to 'new' in scraped_data
    This allows re-sending emails that were previously marked as sent
    """
    try:
        # Update scraped_data
        # Set mail_status = 'new', sent_at = null, etc.
        update_data = {
            "mail_status": "new",
            "sent_at": None,
            "gmail_message_id": None,
            "gmail_thread_id": None,
            "error_message": None,
            "retry_count": 0
        }
        
        result = db.table("scraped_data").update(update_data).in_("mail_status", ["email_sent", "sent", "failed"]).execute()
        
        count = len(result.data) if result.data else 0
        
        logger.info(f"✅ Reset {count} emails to 'new' status")
        
        return {
            "success": True,
            "message": f"Successfully reset {count} emails to 'new' status",
            "reset_count": count
        }
    
    except Exception as e:
        logger.error(f"Error resetting sent emails status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to reset sent emails status: {str(e)}")
