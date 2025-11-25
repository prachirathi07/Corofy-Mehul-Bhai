-- ============================================
-- FINAL MIGRATION: Ultra-Simplified 3-Table Architecture
-- Merge everything into scraped_data
-- ============================================

-- Step 1: Add missing fields to scraped_data
-- ============================================

ALTER TABLE scraped_data 
  -- Critical missing fields
  ADD COLUMN IF NOT EXISTS company_country VARCHAR(100),
  ADD COLUMN IF NOT EXISTS company_domain VARCHAR(255),
  ADD COLUMN IF NOT EXISTS gmail_message_id VARCHAR(255),
  ADD COLUMN IF NOT EXISTS gmail_thread_id VARCHAR(255),
  ADD COLUMN IF NOT EXISTS sent_at TIMESTAMP WITH TIME ZONE,
  
  -- Email queue fields (replaces email_queue table)
  ADD COLUMN IF NOT EXISTS scheduled_time TIMESTAMP WITH TIME ZONE,
  ADD COLUMN IF NOT EXISTS email_timezone VARCHAR(100),
  ADD COLUMN IF NOT EXISTS email_priority INTEGER DEFAULT 0,
  
  -- Failed email fields (replaces failed_emails table)
  ADD COLUMN IF NOT EXISTS error_message TEXT,
  ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS next_retry_at TIMESTAMP WITH TIME ZONE,
  
  -- Personalization tracking
  ADD COLUMN IF NOT EXISTS is_personalized BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS company_website_used BOOLEAN DEFAULT FALSE;

-- Step 2: Auto-populate company_domain from company_website
-- ============================================

UPDATE scraped_data 
SET company_domain = REGEXP_REPLACE(
  REGEXP_REPLACE(company_website, '^https?://', ''),
  '/.*$', ''
)
WHERE company_website IS NOT NULL 
  AND company_domain IS NULL;

-- Step 3: Create indexes for new fields
-- ============================================

CREATE INDEX IF NOT EXISTS idx_scraped_data_company_country 
  ON scraped_data(company_country);

CREATE INDEX IF NOT EXISTS idx_scraped_data_company_domain 
  ON scraped_data(company_domain);

CREATE INDEX IF NOT EXISTS idx_scraped_data_gmail_message_id 
  ON scraped_data(gmail_message_id);

CREATE INDEX IF NOT EXISTS idx_scraped_data_gmail_thread_id 
  ON scraped_data(gmail_thread_id);

CREATE INDEX IF NOT EXISTS idx_scraped_data_sent_at 
  ON scraped_data(sent_at);

CREATE INDEX IF NOT EXISTS idx_scraped_data_scheduled_time 
  ON scraped_data(scheduled_time)
  WHERE mail_status IN ('scheduled', 'sending');

CREATE INDEX IF NOT EXISTS idx_scraped_data_retry 
  ON scraped_data(next_retry_at)
  WHERE mail_status = 'failed' AND retry_count < 3;

-- Step 4: Migrate data from email_queue (if exists)
-- ============================================

DO $$
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'email_queue') THEN
    -- Update scraped_data with queue information
    UPDATE scraped_data sd
    SET 
      scheduled_time = eq.scheduled_time,
      email_timezone = eq.timezone,
      email_priority = eq.priority,
      mail_status = CASE 
        WHEN eq.status = 'pending' THEN 'scheduled'
        WHEN eq.status = 'sending' THEN 'sending'
        WHEN eq.status = 'sent' THEN 'sent'
        WHEN eq.status = 'failed' THEN 'failed'
        ELSE eq.status
      END,
      error_message = eq.error_message,
      retry_count = eq.retry_count
    FROM email_queue eq
    WHERE sd.id = eq.lead_id
      AND eq.status IN ('pending', 'sending');
    
    RAISE NOTICE 'Migrated email_queue data to scraped_data';
  END IF;
END $$;

-- Step 5: Migrate data from failed_emails (if exists)
-- ============================================

DO $$
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'failed_emails') THEN
    -- Update scraped_data with failed email information
    UPDATE scraped_data sd
    SET 
      mail_status = 'failed',
      error_message = fe.error_message,
      retry_count = fe.attempt_count,
      next_retry_at = fe.next_retry_at
    FROM failed_emails fe
    WHERE sd.id = fe.lead_id
      AND fe.status IN ('pending', 'retrying');
    
    RAISE NOTICE 'Migrated failed_emails data to scraped_data';
  END IF;
END $$;

-- Step 6: Migrate data from emails_sent (if exists)
-- ============================================

DO $$
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'emails_sent') THEN
    -- Update scraped_data with sent email information
    UPDATE scraped_data sd
    SET 
      gmail_message_id = es.gmail_message_id,
      gmail_thread_id = es.gmail_thread_id,
      sent_at = es.sent_at,
      is_personalized = es.is_personalized,
      company_website_used = es.company_website_used,
      mail_status = 'sent'
    FROM (
      -- Get the most recent email for each lead
      SELECT DISTINCT ON (lead_id)
        lead_id,
        gmail_message_id,
        gmail_thread_id,
        sent_at,
        is_personalized,
        company_website_used
      FROM emails_sent
      WHERE status = 'SENT' OR status = 'sent'
      ORDER BY lead_id, sent_at DESC
    ) es
    WHERE sd.id = es.lead_id;
    
    RAISE NOTICE 'Migrated emails_sent data to scraped_data';
  END IF;
END $$;

-- Step 7: Drop redundant tables
-- ============================================

DROP TABLE IF EXISTS email_queue CASCADE;
DROP TABLE IF EXISTS failed_emails CASCADE;
DROP TABLE IF EXISTS emails_sent CASCADE;
DROP TABLE IF EXISTS email_replies CASCADE;
DROP TABLE IF EXISTS follow_ups CASCADE;
DROP TABLE IF EXISTS email_batches CASCADE;
DROP TABLE IF EXISTS daily_email_tracking CASCADE;
DROP TABLE IF EXISTS leads CASCADE;
DROP TABLE IF EXISTS email_campaigns CASCADE;
DROP VIEW IF EXISTS active_email_batches CASCADE;
DROP VIEW IF EXISTS scheduled_emails CASCADE;
DROP VIEW IF EXISTS failed_emails_view CASCADE;

-- Step 8: Add column comments

-- ============================================

COMMENT ON COLUMN scraped_data.company_country IS 
  'Company country for timezone-aware email scheduling';

COMMENT ON COLUMN scraped_data.company_domain IS 
  'Extracted domain from company_website (e.g., example.com)';

COMMENT ON COLUMN scraped_data.gmail_message_id IS 
  'Gmail message ID for sent email';

COMMENT ON COLUMN scraped_data.gmail_thread_id IS 
  'Gmail thread ID for reply tracking';

COMMENT ON COLUMN scraped_data.sent_at IS 
  'Timestamp when initial email was sent';

COMMENT ON COLUMN scraped_data.scheduled_time IS 
  'When the email should be sent (for scheduled emails)';

COMMENT ON COLUMN scraped_data.email_timezone IS 
  'Timezone for email scheduling';

COMMENT ON COLUMN scraped_data.email_priority IS 
  'Email priority (higher = sent first)';

COMMENT ON COLUMN scraped_data.error_message IS 
  'Error message if email failed to send';

COMMENT ON COLUMN scraped_data.retry_count IS 
  'Number of retry attempts for failed emails';

COMMENT ON COLUMN scraped_data.next_retry_at IS 
  'When to retry sending this email (for failed emails)';

COMMENT ON COLUMN scraped_data.is_personalized IS 
  'Whether email was personalized using company website';

COMMENT ON COLUMN scraped_data.company_website_used IS 
  'Whether company website was scraped for personalization';

COMMENT ON COLUMN scraped_data.mail_status IS 
  'Email status: new, scheduled, sending, sent, failed, replied';

-- Step 9: Create helper views for common queries
-- ============================================

-- View for scheduled emails (replaces email_queue)
CREATE OR REPLACE VIEW scheduled_emails AS
SELECT 
  id,
  founder_name,
  founder_email,
  company_name,
  email_subject,
  email_content,
  scheduled_time,
  email_timezone,
  email_priority,
  created_at
FROM scraped_data
WHERE mail_status IN ('scheduled', 'sending')
ORDER BY email_priority DESC, scheduled_time ASC;

COMMENT ON VIEW scheduled_emails IS 
  'View of emails waiting to be sent (replaces email_queue table)';

-- View for failed emails (replaces failed_emails)
CREATE OR REPLACE VIEW failed_emails_view AS
SELECT 
  id,
  founder_name,
  founder_email,
  company_name,
  email_subject,
  email_content,
  error_message,
  retry_count,
  next_retry_at,
  created_at,
  CASE 
    WHEN retry_count >= 3 THEN 'max_retries'
    WHEN next_retry_at IS NOT NULL AND next_retry_at > NOW() THEN 'scheduled_retry'
    ELSE 'pending_retry'
  END as retry_status
FROM scraped_data
WHERE mail_status = 'failed'
ORDER BY 
  CASE 
    WHEN next_retry_at IS NOT NULL THEN next_retry_at
    ELSE created_at
  END ASC;

COMMENT ON VIEW failed_emails_view IS 
  'View of failed emails with retry information (replaces failed_emails table)';

-- View for sent emails (replaces emails_sent)
CREATE OR REPLACE VIEW sent_emails_view AS
SELECT 
  id,
  founder_name,
  founder_email,
  company_name,
  email_subject,
  email_content,
  gmail_message_id,
  gmail_thread_id,
  sent_at,
  is_personalized,
  company_website_used,
  mail_replies,
  reply_priority
FROM scraped_data
WHERE mail_status = 'sent'
ORDER BY sent_at DESC;

COMMENT ON VIEW sent_emails_view IS 
  'View of sent emails (replaces emails_sent table)';

-- Step 10: Verify migration
-- ============================================

DO $$
DECLARE
  total_leads INTEGER;
  scheduled_count INTEGER;
  sent_count INTEGER;
  failed_count INTEGER;
  new_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO total_leads FROM scraped_data;
  SELECT COUNT(*) INTO scheduled_count FROM scraped_data WHERE mail_status = 'scheduled';
  SELECT COUNT(*) INTO sent_count FROM scraped_data WHERE mail_status = 'sent';
  SELECT COUNT(*) INTO failed_count FROM scraped_data WHERE mail_status = 'failed';
  SELECT COUNT(*) INTO new_count FROM scraped_data WHERE mail_status = 'new' OR mail_status IS NULL;
  
  RAISE NOTICE '===========================================';
  RAISE NOTICE 'MIGRATION COMPLETE - ULTRA-SIMPLIFIED ARCHITECTURE';
  RAISE NOTICE '===========================================';
  RAISE NOTICE 'Total leads in scraped_data: %', total_leads;
  RAISE NOTICE 'New leads: %', new_count;
  RAISE NOTICE 'Scheduled emails: %', scheduled_count;
  RAISE NOTICE 'Sent emails: %', sent_count;
  RAISE NOTICE 'Failed emails: %', failed_count;
  RAISE NOTICE '===========================================';
END $$;

-- List remaining tables
SELECT 
  table_name,
  pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) as size
FROM information_schema.tables
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- ============================================
-- MIGRATION COMPLETE
-- ============================================
-- 
-- FINAL ARCHITECTURE (3 TABLES):
-- 1. scraped_data (main table - everything)
-- 2. apollo_searches (search tracking)
-- 3. company_websites (website cache)
--
-- TABLES DELETED (10):
-- 1. email_queue (merged into scraped_data)
-- 2. failed_emails (merged into scraped_data)
-- 3. emails_sent (merged into scraped_data)
-- 4. email_replies (merged into scraped_data)
-- 5. follow_ups (merged into scraped_data)
-- 6. email_batches (deleted)
-- 7. daily_email_tracking (deleted)
-- 8. leads (replaced by scraped_data)
-- 9. email_campaigns (not implemented)
-- 10. active_email_batches view (deleted)
--
-- VIEWS CREATED (3):
-- 1. scheduled_emails (replaces email_queue)
-- 2. failed_emails_view (replaces failed_emails)
-- 3. sent_emails_view (replaces emails_sent)
-- ============================================
