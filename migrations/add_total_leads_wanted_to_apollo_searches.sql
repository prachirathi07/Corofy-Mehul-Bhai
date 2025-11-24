-- Add total_leads_wanted column to apollo_searches table
ALTER TABLE apollo_searches
ADD COLUMN IF NOT EXISTS total_leads_wanted INTEGER DEFAULT 0;
