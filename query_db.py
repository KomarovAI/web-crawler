#!/usr/bin/env python3
"""Query database directly from GitHub artifacts"""

import sqlite3
import sys
from pathlib import Path
from typing import Optional

class ArtifactDB:
    """Connect to DB from artifact without downloading"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to database"""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def query(self, sql: str, params: tuple = ()):
        """Execute query"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    
    def get_stats(self) -> dict:
        """Get database statistics"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM pages")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(LENGTH(html)) as size FROM pages")
        size = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) as assets FROM assets")
        assets = cursor.fetchone()[0]
        
        db_size = Path(self.db_path).stat().st_size / 1024 / 1024
        
        return {
            'pages': total,
            'assets': assets,
            'content_size_mb': round(size / 1024 / 1024, 2),
            'db_size_mb': round(db_size, 2)
        }
    
    def get_pages(self, limit: int = 10):
        """Get all pages"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, url, title FROM pages LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def search(self, query: str, limit: int = 10):
        """Search in pages"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, url, title FROM pages WHERE html LIKE ? OR title LIKE ? LIMIT ?",
            (f"%{query}%", f"%{query}%", limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_page_html(self, url: str) -> Optional[str]:
        """Get page HTML"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT html FROM pages WHERE url = ?", (url,))
        row = cursor.fetchone()
        return row[0] if row else None
    
    def close(self):
        """Close connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, *args):
        self.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Query database from artifact')
    parser.add_argument('db_file', help='Path to database file')
    parser.add_argument('--stats', action='store_true', help='Show database stats')
    parser.add_argument('--list', type=int, default=10, help='List N pages')
    parser.add_argument('--search', type=str, help='Search query')
    parser.add_argument('--url', type=str, help='Get page by URL')
    
    args = parser.parse_args()
    
    with ArtifactDB(args.db_file) as db:
        if args.stats:
            stats = db.get_stats()
            print(f"📊 Database Stats:")
            print(f"  Pages: {stats['pages']}")
            print(f"  Assets: {stats['assets']}")
            print(f"  Content size: {stats['content_size_mb']} MB")
            print(f"  DB file size: {stats['db_size_mb']} MB")
        
        elif args.search:
            results = db.search(args.search, args.list)
            print(f"🔍 Search results for '{args.search}':")
            for r in results:
                print(f"  {r['url']}")
        
        elif args.url:
            html = db.get_page_html(args.url)
            if html:
                print(html)
            else:
                print(f"Page not found: {args.url}")
        
        else:
            pages = db.get_pages(args.list)
            print(f"💫 Pages ({args.list}):")
            for p in pages:
                print(f"  {p['url']}")
