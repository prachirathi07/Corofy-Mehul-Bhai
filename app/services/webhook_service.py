"""
Service for sending email data to n8n webhook
"""
import httpx
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class WebhookService:
    """
    Service for sending email data to n8n webhook
    """
    
    def __init__(self):
        self.webhook_url = "https://n8n.srv963601.hstgr.cloud/webhook/5c430cd6-c53b-43bc-9960-1cd16d428991"
        self.timeout = 30.0  # 30 seconds timeout
    
    async def send_email_via_webhook(
        self,
        email_to: str,
        subject: str,
        body: str,
        lead_id: Optional[str] = None,
        email_type: Optional[str] = "initial"
    ) -> Dict[str, Any]:
        """
        Send email data to n8n webhook
        
        Args:
            email_to: Recipient email address
            subject: Email subject
            body: Email body
            lead_id: Optional lead ID for tracking
            email_type: Type of email (initial, followup_5day, followup_10day)
        
        Returns:
            Dict with success status and response from webhook
        """
        try:
            # Prepare payload for n8n webhook
            # Format: email_id, subject, body (as requested by user)
            payload = {
                "email_id": email_to,  # email_id as requested
                "subject": subject,     # subject line
                "body": body            # email body
            }
            
            logger.info(f"🚀 WEBHOOK CALL: Sending email data to n8n webhook for {email_to}")
            logger.info(f"📤 WEBHOOK URL: {self.webhook_url}")
            logger.info(f"📦 WEBHOOK PAYLOAD: {payload}")
            logger.info(f"📧 Email subject: {subject[:100]}...")
            logger.info(f"📝 Email body length: {len(body)} characters")
            
            # Send to webhook
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json"
                    }
                )
                
                # Check response
                response.raise_for_status()
                
                # Try to parse response
                try:
                    response_data = response.json()
                except:
                    response_data = {"message": response.text}
                
                logger.info(f"✅ WEBHOOK SUCCESS: Response for {email_to}: Status {response.status_code}")
                logger.info(f"📥 WEBHOOK RESPONSE DATA: {response_data}")
                
                # Check if n8n confirms email was sent
                # Improved response parsing for new n8n workflow format
                is_success = False
                message_id = None
                thread_id = None
                
                # Check response status code
                if response.status_code in [200, 201]:
                    # Check for explicit success flag in response
                    if response_data.get("success") == True:
                        is_success = True
                        message_id = response_data.get("message_id")
                        thread_id = response_data.get("thread_id")
                    # Fallback: check if message_id exists (indicates email was sent)
                    elif response_data.get("message_id"):
                        is_success = True
                        message_id = response_data.get("message_id")
                        thread_id = response_data.get("thread_id")
                    # Legacy fallback: check for success indicators in message
                    elif "success" in str(response_data).lower() or "sent" in str(response_data).lower():
                        is_success = True
                
                # Build webhook response with Gmail IDs if available
                webhook_response = {
                    "success": is_success,
                    "message": response_data.get("message", "Email sent via webhook" if is_success else "Email sending failed"),
                    "timestamp": response_data.get("timestamp")
                }
                
                if message_id:
                    webhook_response["message_id"] = message_id
                if thread_id:
                    webhook_response["thread_id"] = thread_id
                if not is_success:
                    webhook_response["error"] = response_data.get("error", "Unknown error")
                
                logger.info(f"📥 WEBHOOK RESPONSE PARSED: success={is_success}, message_id={message_id}, thread_id={thread_id}")
                
                return {
                    "success": is_success,
                    "webhook_response": webhook_response,
                    "status_code": response.status_code,
                    "message": webhook_response.get("message", "Email sent via webhook" if is_success else "Email sending failed")
                }
        
        except httpx.TimeoutException:
            error_msg = f"Webhook timeout after {self.timeout}s"
            logger.error(f"❌ WEBHOOK TIMEOUT: {error_msg} for {email_to}")
            logger.error(f"❌ WEBHOOK URL was: {self.webhook_url}")
            return {
                "success": False,
                "error": error_msg,
                "webhook_response": None,
                "status_code": None
            }
        
        except httpx.HTTPStatusError as e:
            error_msg = f"Webhook HTTP error {e.response.status_code}: {e.response.text}"
            logger.error(f"❌ WEBHOOK HTTP ERROR: {error_msg} for {email_to}")
            logger.error(f"❌ WEBHOOK URL was: {self.webhook_url}")
            logger.error(f"❌ Response status: {e.response.status_code}")
            logger.error(f"❌ Response text: {e.response.text[:500]}")
            # Try to parse error response
            try:
                error_response = e.response.json()
                logger.error(f"❌ Response JSON: {error_response}")
            except:
                error_response = {"message": e.response.text}
            
            return {
                "success": False,
                "error": error_msg,
                "webhook_response": error_response,  # Return error response as dict, not None
                "status_code": e.response.status_code
            }
        
        except Exception as e:
            error_msg = f"Webhook error: {str(e)}"
            logger.error(f"❌ WEBHOOK EXCEPTION: {error_msg} for {email_to}", exc_info=True)
            logger.error(f"❌ WEBHOOK URL was: {self.webhook_url}")
            return {
                "success": False,
                "error": error_msg,
                "webhook_response": None,
                "status_code": None
            }

