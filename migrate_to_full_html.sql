-- 🔞 MIGRATION: Add html_content column to existing pages table
-- This allows storing COMPLETE HTML for each page

-- Step 1: Add new columns if they don't exist
ALTER TABLE pages ADD COLUMN html_content TEXT DEFAULT NULL;
ALTER TABLE pages ADD COLUMN html_size INTEGER DEFAULT 0;
ALTER TABLE pages ADD COLUMN content_type TEXT DEFAULT 'text/html';

-- Step 2: Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_pages_html_size ON pages(html_size);
CREATE INDEX IF NOT EXISTS idx_pages_content_type ON pages(content_type);

-- Step 3: Verify migration
SELECT 
    COUNT(*) as total_pages,
    COUNT(CASE WHEN html_content IS NOT NULL THEN 1 END) as pages_with_html,
    COUNT(CASE WHEN html_size > 0 THEN 1 END) as pages_with_size,
    SUM(COALESCE(html_size, 0)) / 1024.0 / 1024.0 as total_html_mb
FROM pages;

-- Step 4: Show table structure
PRAGMA table_info(pages);
