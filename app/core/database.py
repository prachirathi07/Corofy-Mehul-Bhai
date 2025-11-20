from supabase import create_client, Client
from app.core.config import settings

class SupabaseClient:
    _instance: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            # Create Supabase client with default settings
            # Note: Supabase Python client doesn't support custom httpx client configuration
            # Timeout issues should be handled at the application level with retries
            cls._instance = create_client(
                settings.SUPABASE_URL, 
                settings.SUPABASE_KEY
            )
        return cls._instance

# Convenience function
def get_db() -> Client:
    return SupabaseClient.get_client()

