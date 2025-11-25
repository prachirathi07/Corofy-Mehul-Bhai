"""
Dead Letter Queue (DLQ) service for managing failed email attempts.
Automatically retries failed emails with exponential backoff.
Rewritten to use scraped_data table directly in the simplified architecture.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from supabase import Client
import logging
import pytz

logger = logging.getLogger(__name__)

class DeadLetterQueueService:
    """Service for managing failed email attempts and retries using scraped_data"""
    
    def __init__(self, db: Client):
        self.db = db
        self.max_attempts = 3
        self.retry_delays = [3600, 7200, 14400]  # 1h, 2h, 4h in seconds
    
    async def add_failed_email(
        self,
        lead_id: str,
        email_to: str,
        subject: str,
        body: str,
        error: Exception,
        error_type: str = "unknown"
    ) -> Optional[str]:
        """
        Mark an email as failed in scraped_data and schedule retry.
        
        Args:
            lead_id: Lead UUID
            email_to: Recipient email (unused, using lead_id)
            subject: Email subject (unused, using lead_id)
            body: Email body (unused, using lead_id)
            error: Exception that caused the failure
            error_type: Type of error
        
        Returns:
            Lead ID if successful, None otherwise
        """
        try:
            # Calculate next retry time (1 hour from now for first attempt)
            next_retry = datetime.utcnow() + timedelta(seconds=self.retry_delays[0])
            
            # Update scraped_data
            # We use retry_count = 1 for the first failure
            update_data = {
                "mail_status": "failed",
                "error_message": f"{error_type}: {str(error)}",
                "retry_count": 1,
                "next_retry_at": next_retry.isoformat()
            }
            
            self.db.table("scraped_data").update(update_data).eq("id", lead_id).execute()
            
            logger.info(
                f"📥 Added failed email to DLQ (scraped_data): Lead {lead_id} "
                f"(Error: {error_type}, Retry at: {next_retry})"
            )
            
            return lead_id
            
        except Exception as e:
            logger.error(f"Failed to add email to DLQ: {e}", exc_info=True)
            return None
    
    async def retry_failed_emails(self) -> Dict[str, Any]:
        """
        Retry all pending failed emails that are ready for retry.
        Queries scraped_data for mail_status='failed' and next_retry_at <= now.
        
        Returns:
            Dict with retry statistics
        """
        try:
            logger.info("🔄 Processing dead letter queue (scraped_data)...")
            
            now = datetime.utcnow().isoformat()
            
            # Get emails ready for retry
            # mail_status = 'failed' AND next_retry_at <= now
            result = (
                self.db.table("scraped_data")
                .select("*")
                .eq("mail_status", "failed")
                .lte("next_retry_at", now)
                .execute()
            )
            
            if not result.data:
                logger.info("📭 No emails ready for retry")
                return {
                    "success": True,
                    "processed": 0,
                    "succeeded": 0,
                    "failed": 0
                }
            
            retry_emails = result.data
            logger.info(f"📬 Found {len(retry_emails)} emails ready for retry")
            
            processed = 0
            succeeded = 0
            failed = 0
            
            # Import here to avoid circular dependency
            from app.services.email_sending_service import EmailSendingService
            email_service = EmailSendingService(self.db)
            
            for lead in retry_emails:
                try:
                    lead_id = lead["id"]
                    retry_count = lead.get("retry_count", 0) or 0
                    
                    # Mark as processing/retrying (optional, but good for locking)
                    # We can just let EmailSendingService handle the update to 'email_sent' or 'failed'
                    
                    # Attempt to send email
                    # We need to regenerate email content or use what's stored?
                    # EmailSendingService.send_email_to_lead generates content.
                    # Let's use that.
                    
                    logger.info(f"🔄 Retrying lead {lead_id} (Attempt {retry_count + 1})")
                    
                    result = await email_service.send_email_to_lead(
                        lead_id=lead_id,
                        email_type="initial" # Assuming initial for now, could be stored in DB
                    )
                    
                    processed += 1
                    
                    if result.get("success"):
                        # Success! EmailSendingService updates mail_status to 'email_sent'
                        succeeded += 1
                        logger.info(f"✅ DLQ retry succeeded for lead {lead_id}")
                    else:
                        # Failed again
                        new_retry_count = retry_count + 1
                        error_msg = result.get("error", "Unknown error")
                        
                        if new_retry_count >= self.max_attempts:
                            # Max attempts reached - mark as permanently failed (bounced or just failed with no retry)
                            self.db.table("scraped_data").update({
                                "mail_status": "bounced", # Using 'bounced' as permanent failure state
                                "error_message": f"Max retries reached. Last error: {error_msg}",
                                "retry_count": new_retry_count,
                                "next_retry_at": None # No more retries
                            }).eq("id", lead_id).execute()
                            
                            failed += 1
                            logger.warning(
                                f"❌ DLQ max attempts reached for lead {lead_id} "
                                f"({new_retry_count}/{self.max_attempts})"
                            )
                        else:
                            # Schedule next retry
                            delay_index = min(new_retry_count - 1, len(self.retry_delays) - 1)
                            next_retry = datetime.utcnow() + timedelta(
                                seconds=self.retry_delays[delay_index]
                            )
                            
                            self.db.table("scraped_data").update({
                                "mail_status": "failed",
                                "error_message": error_msg,
                                "retry_count": new_retry_count,
                                "next_retry_at": next_retry.isoformat()
                            }).eq("id", lead_id).execute()
                            
                            failed += 1
                            logger.info(
                                f"⏳ DLQ retry failed, rescheduled lead {lead_id} "
                                f"(Attempt {new_retry_count}/{self.max_attempts}, "
                                f"Next retry: {next_retry})"
                            )
                
                except Exception as e:
                    logger.error(f"Error retrying DLQ lead {lead.get('id')}: {e}")
                    failed += 1
            
            logger.info(
                f"📊 DLQ processing complete: {processed} processed, "
                f"{succeeded} succeeded, {failed} failed"
            )
            
            return {
                "success": True,
                "processed": processed,
                "succeeded": succeeded,
                "failed": failed
            }
            
        except Exception as e:
            logger.error(f"Error processing DLQ: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "processed": 0,
                "succeeded": 0,
                "failed": 0
            }
    
    def get_dlq_stats(self) -> Dict[str, Any]:
        """Get DLQ statistics from scraped_data"""
        try:
            # Count failed emails
            failed_result = self.db.table("scraped_data").select("id", count="exact").eq("mail_status", "failed").execute()
            total_failed = failed_result.count if failed_result.count else 0
            
            # Count bounced (permanently failed)
            bounced_result = self.db.table("scraped_data").select("id", count="exact").eq("mail_status", "bounced").execute()
            total_bounced = bounced_result.count if bounced_result.count else 0
            
            return {
                "total_failed": total_failed,
                "pending_retry": total_failed, # All 'failed' are pending retry unless max reached (which moves to bounced)
                "permanently_failed": total_bounced,
                "resolved": 0, # Hard to track resolved historically without separate table
                "by_error_type": {} # Not easily available without group by query
            }
            
        except Exception as e:
            logger.error(f"Error getting DLQ stats: {e}")
            return {}
