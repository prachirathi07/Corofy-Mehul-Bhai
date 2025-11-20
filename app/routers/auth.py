from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()

# OAuth scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

@router.get("/gmail/authorize")
async def gmail_authorize():
    """
    Initiate Gmail OAuth flow
    Redirects user to Google OAuth consent screen
    """
    try:
        if not settings.GMAIL_CLIENT_ID or not settings.GMAIL_CLIENT_SECRET:
            raise HTTPException(
                status_code=400,
                detail="Gmail credentials not configured. Please add GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET to .env"
            )
        
        # Create OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GMAIL_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [
                        f"{settings.API_BASE_URL or 'http://localhost:8000'}/api/auth/gmail/callback",
                        "https://developers.google.com/oauthplayground"
                    ]
                }
            },
            scopes=SCOPES,
            redirect_uri=f"{settings.API_BASE_URL or 'http://localhost:8000'}/api/auth/gmail/callback"
        )
        
        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent to get refresh token
        )
        
        # Store state in session or return it (you might want to use sessions)
        # For now, we'll return the URL and user can complete the flow
        return {
            "authorization_url": authorization_url,
            "state": state,
            "message": "Visit the authorization_url in your browser to complete OAuth"
        }
    
    except Exception as e:
        logger.error(f"Error initiating Gmail OAuth: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to initiate OAuth: {str(e)}")

@router.get("/gmail/callback")
async def gmail_callback(code: str, state: str = None):
    """
    OAuth callback endpoint
    Receives authorization code and exchanges it for tokens
    """
    try:
        if not settings.GMAIL_CLIENT_ID or not settings.GMAIL_CLIENT_SECRET:
            raise HTTPException(
                status_code=400,
                detail="Gmail credentials not configured"
            )
        
        # Create OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GMAIL_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [
                        f"{settings.API_BASE_URL or 'http://localhost:8000'}/api/auth/gmail/callback",
                        "https://developers.google.com/oauthplayground"
                    ]
                }
            },
            scopes=SCOPES,
            redirect_uri=f"{settings.API_BASE_URL or 'http://localhost:8000'}/api/auth/gmail/callback"
        )
        
        # Exchange authorization code for tokens
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Return tokens (user should save refresh_token to .env)
        return {
            "success": True,
            "message": "OAuth successful! Save these to your .env file:",
            "refresh_token": credentials.refresh_token,
            "client_id": settings.GMAIL_CLIENT_ID,
            "client_secret": settings.GMAIL_CLIENT_SECRET,
            "instructions": "Add GMAIL_REFRESH_TOKEN to your .env file with the refresh_token value above"
        }
    
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": "OAuth callback failed. Please try again."
        }

