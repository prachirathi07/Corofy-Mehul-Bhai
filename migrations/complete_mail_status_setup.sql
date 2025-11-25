-- ============================================
-- COMPLETE DATABASE SCHEMA - MAIL_STATUS & FAILED EMAILS
-- ============================================

-- ============================================
-- PART 1: SET DEFAULT VALUES
-- ============================================

-- Set default mail_status to 'new' for future inserts
ALTER TABLE scraped_data 
  ALTER COLUMN mail_status SET DEFAULT 'new';

-- Set default is_verified to false for future inserts
ALTER TABLE scraped_data 
  ALTER COLUMN is_verified SET DEFAULT false;

-- Update existing NULL mail_status values to 'new'
UPDATE scraped_data 
SET mail_status = 'new' 
WHERE mail_status IS NULL;

-- ============================================
-- PART 2: MAIL_STATUS ENUM (OPTIONAL - For Data Integrity)
-- ============================================

-- Create ENUM type for mail_status
DO $$ 
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'mail_status_enum') THEN
    CREATE TYPE mail_status_enum AS ENUM (
      'new',                  -- Default - lead not contacted
      'email_sent',           -- Initial email sent successfully
      'reply_received',       -- Lead replied (terminal state)
      '2nd followup sent',    -- 10-day follow-up sent
      'bounced',              -- Email bounced (planned)
      'unsubscribed'          -- Lead unsubscribed (planned)
    );
  END IF;
END $$;

-- Optionally convert mail_status column to ENUM (run only if you want strict validation)
-- ALTER TABLE scraped_data 
--   ALTER COLUMN mail_status TYPE mail_status_enum 
--   USING mail_status::mail_status_enum;

-- ============================================
-- PART 3: FAILED EMAILS TABLE (If not exists)
-- ============================================

-- Create failed_emails table for Dead Letter Queue (DLQ)
CREATE TABLE IF NOT EXISTS failed_emails (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID REFERENCES scraped_data(id) ON DELETE CASCADE,
  email_to VARCHAR(255) NOT NULL,
  subject TEXT NOT NULL,
  body TEXT NOT NULL,
  error_message TEXT,
  error_type VARCHAR(50),  -- 'network', 'validation', 'api_error', 'rate_limit', etc.
  attempt_count INTEGER DEFAULT 1,
  max_attempts INTEGER DEFAULT 3,
  status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'retrying', 'resolved', 'failed'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_attempt_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  next_retry_at TIMESTAMP WITH TIME ZONE,
  resolved_at TIMESTAMP WITH TIME ZONE,
  metadata JSONB DEFAULT '{}'
);

-- Create indexes for failed_emails
CREATE INDEX IF NOT EXISTS idx_failed_emails_status 
  ON failed_emails(status) 
  WHERE status IN ('pending', 'retrying');

CREATE INDEX IF NOT EXISTS idx_failed_emails_next_retry 
  ON failed_emails(next_retry_at) 
  WHERE status = 'pending' AND next_retry_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_failed_emails_lead_id 
  ON failed_emails(lead_id);

CREATE INDEX IF NOT EXISTS idx_failed_emails_created 
  ON failed_emails(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_failed_emails_error_type 
  ON failed_emails(error_type);

-- ============================================
-- PART 4: HELPER VIEWS
-- ============================================

-- View for emails ready to retry
CREATE OR REPLACE VIEW retry_ready_emails AS
SELECT 
  id,
  lead_id,
  email_to,
  subject,
  body,
  error_message,
  error_type,
  attempt_count,
  max_attempts,
  next_retry_at,
  created_at
FROM failed_emails
WHERE status = 'pending'
  AND next_retry_at <= NOW()
  AND attempt_count < max_attempts
ORDER BY next_retry_at ASC;

COMMENT ON VIEW retry_ready_emails IS 
  'Emails in DLQ that are ready for retry';

-- View for failed emails summary
CREATE OR REPLACE VIEW failed_emails_summary AS
SELECT 
  status,
  error_type,
  COUNT(*) as count,
  MIN(created_at) as oldest_failure,
  MAX(created_at) as latest_failure,
  AVG(attempt_count) as avg_attempts
FROM failed_emails
GROUP BY status, error_type
ORDER BY count DESC;

COMMENT ON VIEW failed_emails_summary IS 
  'Summary statistics for failed emails by status and error type';

-- ============================================
-- PART 5: MAIL_STATUS VALIDATION FUNCTION
-- ============================================

-- Function to validate mail_status values
CREATE OR REPLACE FUNCTION validate_mail_status()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.mail_status NOT IN (
    'new', 
    'email_sent', 
    'reply_received', 
    '2nd followup sent', 
    'bounced', 
    'unsubscribed'
  ) THEN
    RAISE EXCEPTION 'Invalid mail_status value: %. Must be one of: new, email_sent, reply_received, 2nd followup sent, bounced, unsubscribed', 
      NEW.mail_status;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for mail_status validation (optional)
-- DROP TRIGGER IF EXISTS validate_mail_status_trigger ON scraped_data;
-- CREATE TRIGGER validate_mail_status_trigger
--   BEFORE INSERT OR UPDATE ON scraped_data
--   FOR EACH ROW
--   EXECUTE FUNCTION validate_mail_status();

-- ============================================
-- PART 6: QUERY TEMPLATES
-- ============================================

-- Query 1: Get leads ready for email sending
-- (verified, not sent, has email)
COMMENT ON TABLE scraped_data IS 
  'Main leads table. Use this query to get leads ready for email:
  
  SELECT * FROM scraped_data
  WHERE is_verified = true
    AND founder_email IS NOT NULL
    AND founder_email != ''''
    AND mail_status NOT IN (''email_sent'', ''reply_received'', ''2nd followup sent'')
    AND (email_processed IS NULL OR email_processed = false)
  LIMIT 10;';

-- Query 2: Get failed emails ready for retry
-- SELECT * FROM retry_ready_emails;

-- Query 3: Get failed emails statistics
-- SELECT * FROM failed_emails_summary;

-- ============================================
-- PART 7: VERIFICATION QUERIES
-- ============================================

-- Verify mail_status distribution
SELECT 
  mail_status,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM scraped_data
GROUP BY mail_status
ORDER BY count DESC;

-- Verify email sending eligibility
SELECT 
  COUNT(*) as total_leads,
  COUNT(CASE WHEN is_verified = true THEN 1 END) as verified_leads,
  COUNT(CASE WHEN founder_email IS NOT NULL AND founder_email != '' THEN 1 END) as has_email,
  COUNT(CASE WHEN mail_status = 'new' THEN 1 END) as new_leads,
  COUNT(CASE WHEN mail_status = 'email_sent' THEN 1 END) as sent_leads,
  COUNT(CASE WHEN mail_status = 'reply_received' THEN 1 END) as replied_leads,
  COUNT(CASE 
    WHEN is_verified = true 
    AND founder_email IS NOT NULL 
    AND founder_email != ''
    AND mail_status NOT IN ('email_sent', 'reply_received', '2nd followup sent')
    AND (email_processed IS NULL OR email_processed = false)
    THEN 1 
  END) as eligible_for_sending
FROM scraped_data;

-- Verify failed emails
SELECT 
  status,
  error_type,
  COUNT(*) as count,
  AVG(attempt_count) as avg_attempts
FROM failed_emails
GROUP BY status, error_type
ORDER BY count DESC;

-- ============================================
-- EXECUTION SUMMARY
-- ============================================

DO $$
DECLARE
  total_leads INTEGER;
  eligible_leads INTEGER;
  failed_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO total_leads FROM scraped_data;
  
  SELECT COUNT(*) INTO eligible_leads 
  FROM scraped_data
  WHERE is_verified = true 
    AND founder_email IS NOT NULL 
    AND founder_email != ''
    AND mail_status NOT IN ('email_sent', 'reply_received', '2nd followup sent')
    AND (email_processed IS NULL OR email_processed = false);
  
  SELECT COUNT(*) INTO failed_count FROM failed_emails WHERE status IN ('pending', 'retrying');
  
  RAISE NOTICE '===========================================';
  RAISE NOTICE 'DATABASE SETUP COMPLETE';
  RAISE NOTICE '===========================================';
  RAISE NOTICE 'Total leads: %', total_leads;
  RAISE NOTICE 'Eligible for email sending: %', eligible_leads;
  RAISE NOTICE 'Failed emails pending retry: %', failed_count;
  RAISE NOTICE '===========================================';
  RAISE NOTICE 'Default mail_status: new';
  RAISE NOTICE 'Default is_verified: false';
  RAISE NOTICE '===========================================';
END $$;

-- ============================================
-- NOTES:
-- ============================================
-- 
-- MAIL_STATUS VALUES:
-- - 'new': Lead not contacted yet (default)
-- - 'email_sent': Initial email sent successfully
-- - 'reply_received': Lead replied (terminal state)
-- - '2nd followup sent': 10-day follow-up sent
-- - 'bounced': Email bounced (planned, not implemented)
-- - 'unsubscribed': Lead opted out (planned, not implemented)
--
-- FAILED EMAIL HANDLING:
-- - Failed emails go to 'failed_emails' table (Dead Letter Queue)
-- - Automatic retry with exponential backoff: 1h, 2h, 4h
-- - Max 3 retry attempts
-- - Status: 'pending' → 'retrying' → 'resolved' or 'failed'
-- - Use 'retry_ready_emails' view to see emails ready for retry
--
-- FOREIGN KEY REFERENCES:
-- - failed_emails.lead_id → scraped_data.id (ON DELETE CASCADE)
-- - All references are properly set up
-- ============================================
