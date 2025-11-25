"""
Service for checking email replies and analyzing them
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.gmail_service import GmailService
from app.services.openai_service import OpenAIService
from app.core.database import SupabaseClient
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

class ReplyService:
    """
    Service for checking and analyzing email replies
    """
    
    def __init__(self):
        self.db = SupabaseClient.get_client()
        self._gmail_service = None
        self.openai_service = OpenAIService()
    
    @property
    def gmail_service(self):
        """Lazy load Gmail service"""
        if self._gmail_service is None:
            try:
                self._gmail_service = GmailService()
            except Exception as e:
                logger.warning(f"Gmail service not available: {e}")
                return None
        return self._gmail_service
    
    async def check_and_analyze_replies(self) -> Dict[str, Any]:
        """
        Check for new replies and analyze them
        This should be called every 15 minutes
        
        Returns:
            Dict with processing results
        """
        try:
            if not self.gmail_service:
                return {
                    "success": False,
                    "error": "Gmail service not available",
                    "checked": 0,
                    "new_replies": 0,
                    "analyzed": 0
                }
            
            # Get all sent emails with thread_id that haven't been marked as replied
            # Check scraped_data table
            # We look for leads that have been sent an email but haven't replied yet
            sent_leads = (
                self.db.table("scraped_data")
                .select("*")
                .not_.is_("gmail_thread_id", "null")
                .in_("mail_status", ["email_sent", "sent", "2nd followup sent"])
                .execute()
            )
            
            if not sent_leads.data:
                return {
                    "success": True,
                    "checked": 0,
                    "new_replies": 0,
                    "analyzed": 0,
                    "message": "No sent leads with thread IDs to check"
                }
            
            checked = 0
            new_replies = 0
            analyzed = 0
            skipped = 0
            
            for lead in sent_leads.data:
                try:
                    lead_id = lead["id"]
                    thread_id = lead.get("gmail_thread_id")
                    original_message_id = lead.get("gmail_message_id")
                    
                    if not thread_id:
                        continue
                    
                    checked += 1
                    
                    # Get thread messages from Gmail
                    thread_messages = self.gmail_service.get_thread_messages(thread_id)
                    
                    if not thread_messages:
                        continue
                    
                    # Find replies (messages that are not the original sent email)
                    replies = []
                    
                    for message in thread_messages:
                        msg_id = message.get("id")
                        # Skip the original message if we know it
                        if original_message_id and msg_id == original_message_id:
                            continue
                        
                        # Check if this is a reply (has headers indicating it's a reply)
                        headers = message.get("payload", {}).get("headers", [])
                        in_reply_to = None
                        from_email = None
                        
                        for header in headers:
                            name = header.get("name", "").lower()
                            if name == "in-reply-to":
                                in_reply_to = header.get("value")
                            elif name == "from":
                                from_email = header.get("value")
                        
                        # Simple check: if it's not from us (assuming we are not the sender of the reply)
                        # Ideally we should check if from_email is NOT our email.
                        # But for now, if it's in the thread and not the original message, treat as reply candidate.
                        # Better check: if in_reply_to is present, it's likely a reply.
                        
                        if in_reply_to or (original_message_id and msg_id != original_message_id):
                            replies.append(message)
                    
                    if not replies:
                        continue
                        
                    # We found replies!
                    # Get the latest reply
                    latest_reply = replies[-1]
                    
                    # Extract reply data
                    reply_data = self._extract_reply_data(latest_reply, lead_id)
                    
                    if reply_data:
                        new_replies += 1
                        
                        # Analyze the reply
                        analysis_result = await self._analyze_reply(reply_data, lead_id)
                        if analysis_result.get("success"):
                            analyzed += 1
                
                except Exception as e:
                    logger.error(f"Error checking replies for lead {lead.get('id')}: {e}", exc_info=True)
                    continue
            
            logger.info(f"📧 Reply check completed: {checked} checked, {new_replies} new replies, {analyzed} analyzed")
            
            return {
                "success": True,
                "checked": checked,
                "new_replies": new_replies,
                "analyzed": analyzed,
                "skipped": skipped
            }
        
        except Exception as e:
            logger.error(f"Error checking replies: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "checked": 0,
                "new_replies": 0,
                "analyzed": 0
            }
    
    def _extract_reply_data(self, message: Dict[str, Any], lead_id: str) -> Optional[Dict[str, Any]]:
        """
        Extract reply data from Gmail message
        """
        try:
            payload = message.get("payload", {})
            headers = payload.get("headers", [])
            
            # Extract headers
            reply_from = None
            reply_subject = None
            reply_date = None
            
            for header in headers:
                name = header.get("name", "").lower()
                value = header.get("value", "")
                
                if name == "from":
                    reply_from = value
                elif name == "subject":
                    reply_subject = value
                elif name == "date":
                    reply_date = value
            
            # Extract body
            reply_body = self._extract_message_body(payload)
            
            if not reply_body:
                return None
            
            # Parse date
            try:
                from email.utils import parsedate_to_datetime
                if reply_date:
                    parsed_date = parsedate_to_datetime(reply_date)
                    reply_date_iso = parsed_date.isoformat()
                else:
                    reply_date_iso = datetime.utcnow().isoformat()
            except:
                reply_date_iso = datetime.utcnow().isoformat()
            
            return {
                "lead_id": lead_id,
                "gmail_message_id": message.get("id"),
                "gmail_thread_id": message.get("threadId"),
                "reply_from": reply_from or "unknown",
                "reply_subject": reply_subject or "",
                "reply_body": reply_body,
                "reply_date": reply_date_iso
            }
        
        except Exception as e:
            logger.error(f"Error extracting reply data: {e}", exc_info=True)
            return None
    
    def _extract_message_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract message body from Gmail payload
        """
        try:
            body = ""
            
            # Check if body is in payload directly
            if "body" in payload and payload["body"].get("data"):
                import base64
                body_data = payload["body"].get("data")
                body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
            
            # Check parts (multipart messages)
            if "parts" in payload:
                for part in payload["parts"]:
                    mime_type = part.get("mimeType", "")
                    if mime_type == "text/plain" or mime_type == "text/html":
                        if part.get("body", {}).get("data"):
                            import base64
                            part_data = part["body"]["data"]
                            part_body = base64.urlsafe_b64decode(part_data).decode('utf-8', errors='ignore')
                            if part_body:
                                body = part_body
                                break
            
            return body
        
        except Exception as e:
            logger.error(f"Error extracting message body: {e}", exc_info=True)
            return ""
    
    async def _analyze_reply(self, reply_data: Dict[str, Any], lead_id: str) -> Dict[str, Any]:
        """
        Analyze a reply using OpenAI to get summary and priority
        """
        try:
            reply_body = reply_data.get("reply_body", "")
            reply_subject = reply_data.get("reply_subject", "")
            
            if not reply_body:
                return {"success": False, "error": "No reply body to analyze"}
            
            # Use OpenAI to analyze the reply
            analysis_prompt = f"""Analyze the following email reply and provide:
1. A brief summary (2-3 sentences)
2. Priority level: "high", "medium", or "low"
   - High: Interested, wants to proceed, asking for next steps, positive response
   - Medium: Neutral, asking questions, needs more information
   - Low: Not interested, negative response, unsubscribe request

Reply Subject: {reply_subject}
Reply Body: {reply_body[:2000]}

Return your response as JSON with keys: "summary" and "priority"."""
            
            try:
                # Call OpenAI
                response = await asyncio.to_thread(
                    lambda: self.openai_service.client.chat.completions.create(
                        model=self.openai_service.model,
                        messages=[
                            {"role": "system", "content": "You are an expert at analyzing business email replies. Return JSON only."},
                            {"role": "user", "content": analysis_prompt}
                        ],
                        response_format={"type": "json_object"},
                        max_tokens=500,
                        temperature=0.3
                    )
                )
                
                result_text = response.choices[0].message.content.strip()
                analysis = json.loads(result_text)
                
                summary = analysis.get("summary", "")
                priority = analysis.get("priority", "medium").lower()
                
                # Validate priority
                if priority not in ["high", "medium", "low"]:
                    priority = "medium"
                
                # Update scraped_data with summary and priority
                update_data = {
                    "mail_status": "reply_received",
                    "reply_priority": priority,
                    "mail_replies": summary  # Store summary in mail_replies column
                }
                
                self.db.table("scraped_data").update(update_data).eq("id", lead_id).execute()
                
                logger.info(f"✅ Analyzed reply for lead {lead_id}: Priority={priority}")
                
                return {
                    "success": True,
                    "summary": summary,
                    "priority": priority
                }
            
            except Exception as e:
                logger.error(f"Error analyzing reply with OpenAI: {e}", exc_info=True)
                # Still update status to reply_received even if analysis fails
                self.db.table("scraped_data").update({
                    "mail_status": "reply_received"
                }).eq("id", lead_id).execute()
                
                return {
                    "success": False,
                    "error": str(e),
                    "status_updated": True
                }
        
        except Exception as e:
            logger.error(f"Error in _analyze_reply: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
