"""
Script to reset all sent emails back to 'generated' status
"""
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    sys.exit(1)

# Create Supabase client
db: Client = create_client(supabase_url, supabase_key)

try:
    # Find all emails with status 'sent'
    print("🔍 Finding all emails with 'sent' status...")
    sent_emails = (
        db.table("emails_sent")
        .select("id")
        .eq("status", "sent")
        .execute()
    )
    
    if not sent_emails.data:
        print("✅ No emails with 'sent' status found")
        sys.exit(0)
    
    email_ids = [email["id"] for email in sent_emails.data]
    count = len(email_ids)
    
    print(f"📧 Found {count} emails with 'sent' status")
    print("🔄 Resetting status to 'generated'...")
    
    # Update all sent emails to 'generated' status
    # Set sent_at to a default timestamp (since it's NOT NULL in DB)
    from datetime import datetime
    default_sent_at = datetime.utcnow().isoformat()
    
    updated = 0
    for email_id in email_ids:
        try:
            db.table("emails_sent").update({
                "status": "generated",
                "sent_at": default_sent_at  # Keep a timestamp since DB requires NOT NULL
            }).eq("id", email_id).execute()
            updated += 1
        except Exception as e:
            print(f"⚠️ Error updating email {email_id}: {e}")
    
    print(f"✅ Successfully reset {updated} emails from 'sent' to 'generated' status")
    print(f"📊 Updated: {updated}/{count} emails")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

