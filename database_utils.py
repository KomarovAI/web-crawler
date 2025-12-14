#!/usr/bin/env python3
"""
Database utilities for web crawler
Store and query entire websites from SQLite database
"""

import sqlite3
import hashlib
import json
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime


class WebsiteDatabase:
    """SQLite database for storing complete websites"""

    def __init__(self, db_path: str = "crawled.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn

    def init_db(self):
        """Initialize database schema"""
        schema_path = Path(__file__).parent / "database_schema.sql"
        
        if not schema_path.exists():
            # Create schema inline if file doesn't exist
            self._create_schema_inline()
        else:
            with open(schema_path) as f:
                schema = f.read()
            
            conn = self.get_connection()
            conn.executescript(schema)
            conn.commit()
            conn.close()

    def _create_schema_inline(self):
        """Create schema directly (if file not available)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Pages table
        cursor.execute("""
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
            )
        """)
        
        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pages_md5 ON pages(md5_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pages_crawled ON pages(crawled_at)")
        
        # Assets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER NOT NULL,
                asset_url TEXT NOT NULL,
                asset_type TEXT,
                content BLOB,
                content_length INTEGER,
                md5_hash TEXT,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assets_page ON assets(page_id)")
        
        # Links table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_page_id INTEGER NOT NULL,
                to_url TEXT NOT NULL,
                link_text TEXT,
                link_type TEXT,
                crawled INTEGER DEFAULT 0,
                FOREIGN KEY (from_page_id) REFERENCES pages(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()

    def save_page(self, url: str, html: str, title: str = None, 
                  status_code: int = 200, content_type: str = None,
                  response_time_ms: int = None) -> int:
        """Save page to database"""
        md5_hash = hashlib.md5(html.encode()).hexdigest()
        content_length = len(html.encode())
        
        # Extract text content (simple strip of HTML tags)
        import re
        text_content = re.sub('<[^<]+?>', '', html)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO pages 
                (url, html, title, text_content, status_code, content_type, 
                 content_length, md5_hash, response_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                url, html, title, text_content, status_code, content_type,
                content_length, md5_hash, response_time_ms
            ))
            conn.commit()
            page_id = cursor.lastrowid
            return page_id
        except sqlite3.IntegrityError:
            # Page already exists
            cursor.execute("SELECT id FROM pages WHERE url = ?", (url,))
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def save_asset(self, page_id: int, asset_url: str, content: bytes,
                   asset_type: str = None) -> int:
        """Save asset (image, CSS, JS, etc) to database"""
        md5_hash = hashlib.md5(content).hexdigest()
        content_length = len(content)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO assets 
            (page_id, asset_url, asset_type, content, content_length, md5_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (page_id, asset_url, asset_type, content, content_length, md5_hash))
        
        conn.commit()
        asset_id = cursor.lastrowid
        conn.close()
        
        return asset_id

    def get_page_by_url(self, url: str) -> Optional[Dict]:
        """Get page from database by URL"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM pages WHERE url = ?", (url,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None

    def get_page_html(self, url: str) -> Optional[str]:
        """Get raw HTML of page by URL"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT html FROM pages WHERE url = ?", (url,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None

    def get_all_pages(self, limit: int = None) -> List[Dict]:
        """Get all pages from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if limit:
            cursor.execute("SELECT * FROM pages LIMIT ?", (limit,))
        else:
            cursor.execute("SELECT * FROM pages")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def search_pages(self, query: str) -> List[Dict]:
        """Full-text search in pages"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.* FROM pages p
            WHERE p.html LIKE ? OR p.title LIKE ? OR p.text_content LIKE ?
            ORDER BY p.crawled_at DESC
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def get_page_assets(self, page_id: int) -> List[Dict]:
        """Get all assets for a page"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM assets WHERE page_id = ?
        """, (page_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def get_asset(self, asset_id: int) -> Optional[bytes]:
        """Get asset binary content by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT content FROM assets WHERE id = ?", (asset_id,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None

    def get_page_links(self, page_id: int) -> List[Dict]:
        """Get all links from a page"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM links WHERE from_page_id = ?
        """, (page_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

    def get_stats(self) -> Dict:
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM crawl_stats")
        row = cursor.fetchone()
        
        # Get database file size
        db_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
        
        conn.close()
        
        return {
            **dict(row),
            'database_size_mb': round(db_size / 1024 / 1024, 2),
            'database_file': self.db_path
        }

    def export_as_json(self, output_path: str):
        """Export entire database as JSON"""
        data = {
            'pages': self.get_all_pages(),
            'stats': self.get_stats(),
            'exported_at': datetime.now().isoformat()
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def cleanup_duplicates(self) -> int:
        """Remove duplicate pages based on MD5 hash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM pages WHERE id NOT IN (
                SELECT MIN(id) FROM pages GROUP BY md5_hash
            )
        """)
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted

    def get_database_size_mb(self) -> float:
        """Get database file size in MB"""
        if Path(self.db_path).exists():
            return Path(self.db_path).stat().st_size / 1024 / 1024
        return 0


if __name__ == "__main__":
    # Example usage
    db = WebsiteDatabase("test_crawler.db")
    
    # Save a page
    page_id = db.save_page(
        url="https://example.com",
        html="<html><body>Hello World</body></html>",
        title="Example Page",
        status_code=200,
        content_type="text/html"
    )
    print(f"✅ Saved page with ID: {page_id}")
    
    # Get page
    page = db.get_page_by_url("https://example.com")
    print(f"📄 Page: {page}")
    
    # Get stats
    stats = db.get_stats()
    print(f"📊 Stats: {stats}")
    
    # Search
    results = db.search_pages("Hello")
    print(f"🔍 Search results: {results}")
