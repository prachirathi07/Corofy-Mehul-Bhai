-- Add missing columns to scraped_data table
ALTER TABLE scraped_data
ADD COLUMN IF NOT EXISTS apollo_search_id UUID REFERENCES apollo_searches(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'new',
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_scraped_data_apollo_search_id ON scraped_data(apollo_search_id);
CREATE INDEX IF NOT EXISTS idx_scraped_data_status ON scraped_data(status);
