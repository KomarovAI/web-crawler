-- Web Crawler Database Schema
-- Complete schema for storing entire websites in SQLite

-- Main pages table
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    html TEXT NOT NULL,
    text_content TEXT,
    status_code INTEGER,
    content_type TEXT,
    content_length INTEGER,
    md5_hash TEXT UNIQUE,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP,
    response_time_ms INTEGER,
    error_message TEXT
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url);
CREATE INDEX IF NOT EXISTS idx_pages_md5 ON pages(md5_hash);
CREATE INDEX IF NOT EXISTS idx_pages_crawled ON pages(crawled_at);
CREATE INDEX IF NOT EXISTS idx_pages_title ON pages(title);

-- Assets (images, CSS, JS, etc)
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id INTEGER NOT NULL,
    asset_url TEXT NOT NULL,
    asset_type TEXT,  -- 'image', 'css', 'js', 'font', 'other'
    content BLOB,  -- Binary content
    content_length INTEGER,
    md5_hash TEXT,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_assets_page ON assets(page_id);
CREATE INDEX IF NOT EXISTS idx_assets_url ON assets(asset_url);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(asset_type);

-- Links extraction (internal and external)
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_page_id INTEGER NOT NULL,
    to_url TEXT NOT NULL,
    link_text TEXT,
    link_type TEXT,  -- 'internal', 'external', 'anchor'
    crawled INTEGER DEFAULT 0,  -- 0 = not crawled, 1 = crawled, -1 = error
    FOREIGN KEY (from_page_id) REFERENCES pages(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_links_from ON links(from_page_id);
CREATE INDEX IF NOT EXISTS idx_links_to ON links(to_url);
CREATE INDEX IF NOT EXISTS idx_links_crawled ON links(crawled);

-- Metadata
CREATE TABLE IF NOT EXISTS metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id INTEGER NOT NULL,
    meta_name TEXT,  -- 'description', 'keywords', 'og:title', etc
    meta_content TEXT,
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_metadata_page ON metadata(page_id);
CREATE INDEX IF NOT EXISTS idx_metadata_name ON metadata(meta_name);

-- Crawl sessions
CREATE TABLE IF NOT EXISTS crawl_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_url TEXT NOT NULL,
    max_pages INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    total_pages_crawled INTEGER DEFAULT 0,
    total_assets_downloaded INTEGER DEFAULT 0,
    total_size_bytes INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running',  -- 'running', 'completed', 'failed'
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_started ON crawl_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON crawl_sessions(status);

-- Search index (full-text search)
CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
    url,
    title,
    text_content,
    content=pages,
    content_rowid=id
);

-- Triggers to maintain FTS index
CREATE TRIGGER IF NOT EXISTS pages_fts_insert AFTER INSERT ON pages BEGIN
  INSERT INTO pages_fts(rowid, url, title, text_content) 
  VALUES (new.id, new.url, new.title, new.text_content);
END;

CREATE TRIGGER IF NOT EXISTS pages_fts_delete AFTER DELETE ON pages BEGIN
  DELETE FROM pages_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS pages_fts_update AFTER UPDATE ON pages BEGIN
  DELETE FROM pages_fts WHERE rowid = old.id;
  INSERT INTO pages_fts(rowid, url, title, text_content) 
  VALUES (new.id, new.url, new.title, new.text_content);
END;

-- Statistics view
CREATE VIEW IF NOT EXISTS crawl_stats AS
SELECT 
    (SELECT COUNT(*) FROM pages) as total_pages,
    (SELECT COUNT(*) FROM assets) as total_assets,
    (SELECT SUM(content_length) FROM pages WHERE content_length IS NOT NULL) as total_pages_size,
    (SELECT SUM(content_length) FROM assets WHERE content_length IS NOT NULL) as total_assets_size,
    (SELECT COUNT(*) FROM links WHERE crawled = 1) as crawled_links,
    (SELECT COUNT(*) FROM links WHERE crawled = 0) as uncrawled_links,
    (SELECT COUNT(*) FROM links WHERE crawled = -1) as failed_links,
    (SELECT datetime('now')) as last_update;

-- Query examples:
-- SELECT * FROM pages WHERE url LIKE '%contact%';
-- SELECT * FROM pages_fts WHERE text_content MATCH 'keyword';
-- SELECT from_page_id, COUNT(*) FROM links GROUP BY from_page_id;
-- SELECT * FROM crawl_stats;
