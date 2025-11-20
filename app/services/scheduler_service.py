"""
Scheduler service for processing email queue every 2 hours
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.email_sending_service import EmailSendingService
from app.services.followup_service import FollowUpService
from app.core.database import SupabaseClient
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    """
    Service for scheduling background tasks
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.db = SupabaseClient.get_client()
        self._email_sending_service = None
        self.followup_service = FollowUpService()
    
    @property
    def email_sending_service(self):
        """Lazy load email sending service"""
        if self._email_sending_service is None:
            try:
                self._email_sending_service = EmailSendingService(self.db)
            except Exception as e:
                logger.error(f"Failed to initialize email sending service: {e}")
                return None
        return self._email_sending_service
    
    def start(self):
        """Start the scheduler"""
        # Schedule email queue processing every 2 hours
        self.scheduler.add_job(
            self._process_email_queue,
            trigger=IntervalTrigger(hours=2),
            id='process_email_queue',
            name='Process Email Queue',
            replace_existing=True
        )
        
        # Schedule follow-up processing daily at 9 AM
        from apscheduler.triggers.cron import CronTrigger
        self.scheduler.add_job(
            self._process_followups,
            trigger=CronTrigger(hour=9, minute=0),  # 9 AM daily
            id='process_followups',
            name='Process Due Follow-ups',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Scheduler started:")
        logger.info("  - Email queue processing: Every 2 hours")
        logger.info("  - Follow-up processing: Daily at 9 AM")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    async def _process_email_queue(self):
        """Process email queue (called by scheduler every 2 hours)"""
        try:
            if self.email_sending_service is None:
                logger.warning("Email sending service not available. Skipping queue processing.")
                return
            
            logger.info("🔄 Processing email queue (scheduled task - every 2 hours)")
            result = await self.email_sending_service.process_email_queue()
            logger.info(f"✅ Email queue processed: {result}")
        except Exception as e:
            logger.error(f"❌ Error in scheduled email queue processing: {e}", exc_info=True)
    
    async def _process_followups(self):
        """Process due follow-ups (called by scheduler)"""
        try:
            logger.info("Processing due follow-ups (scheduled task)")
            result = await self.followup_service.process_due_followups()
            logger.info(f"Follow-ups processed: {result}")
        except Exception as e:
            logger.error(f"Error in scheduled follow-up processing: {e}", exc_info=True)

