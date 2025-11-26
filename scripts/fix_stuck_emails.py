
import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db

async def fix_stuck_emails():
    print("🔧 Starting fix for stuck emails...")
    
    db = get_db()
    
    # Find leads that are verified but have no valid mail_status
    # We want to set them to 'scheduled' so the scheduler picks them up
    
    # Fetch all verified leads
    response = db.table("scraped_data").select("*").eq("is_verified", True).execute()
    leads = response.data
    
    print(f"📊 Found {len(leads)} verified leads.")
    
    count = 0
    for lead in leads:
        mail_status = lead.get("mail_status")
        
        # If mail_status is null, pending, or empty, and it's verified, it's likely stuck
        if not mail_status or mail_status == "pending":
            print(f"🔄 Fixing lead {lead.get('id')} ({lead.get('founder_email')}) - Status: {mail_status} -> scheduled")
            
            # Update to scheduled
            db.table("scraped_data").update({
                "mail_status": "scheduled",
                "scheduled_time": datetime.utcnow().isoformat()
            }).eq("id", lead.get("id")).execute()
            
            count += 1
            
    print(f"✅ Fixed {count} stuck leads.")

if __name__ == "__main__":
    asyncio.run(fix_stuck_emails())
