#!/usr/bin/env python3
"""
Production-ready web crawler with:
- Exponential backoff retry logic
- Rate limiting (respects Retry-After headers)
- Proper error handling (no bare except)
- Comprehensive logging
- URL normalization and validation
- Connection pooling
- Memory management
"""

import asyncio
import aiohttp
import logging
import random
import hashlib
from typing import Optional, Set, Dict
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class URLNormalizer:
    """URL normalization and validation utilities"""
    
    @staticmethod
    def normalize(url: str) -> str:
        """Normalize URL to prevent duplicates"""
        try:
            parsed = urlparse(url)
            
            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower()
            path = parsed.path or '/'
            
            if path != '/' and path.endswith('/'):
                path = path.rstrip('/')
            
            params = parse_qs(parsed.query, keep_blank_values=True)
            params = {k: sorted(v) for k, v in sorted(params.items())}
            query = urlencode(params, doseq=True) if params else ''
            
            return f"{scheme}://{netloc}{path}{'?' + query if query else ''}"
        except Exception as e:
            logger.error(f"Error normalizing URL: {e}")
            return url
    
    @staticmethod
    def validate(url: str, allowed_domain: str = None) -> bool:
        """Validate URL before crawling"""
        if not url or len(url) > 2048:
            return False
        
        if not url.startswith(('http://', 'https://')):
            return False
        
        dangerous_schemes = ['javascript:', 'data:', 'mailto:', 'ftp:', 'file:', 'telnet:']
        if any(url.startswith(s) for s in dangerous_schemes):
            return False
        
        try:
            parsed = urlparse(url)
            
            if allowed_domain:
                if parsed.netloc.lower() != allowed_domain.lower():
                    return False
            
            if not parsed.scheme or not parsed.netloc:
                return False
            
            return True
        except Exception:
            return False


class CrawlerDatabase:
    """Production-ready SQLite database for crawler"""
    
    def __init__(self, db_path: str = 'crawler.db'):
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Initialize database schema"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    html TEXT NOT NULL,
                    status_code INTEGER DEFAULT 200,
                    content_length INTEGER,
                    md5_hash TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    response_time_ms INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_pages_md5 ON pages(md5_hash)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_pages_fetched ON pages(fetched_at)
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    error_message TEXT,
                    status_code INTEGER,
                    attempt_count INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def save_page(self, url: str, html: str, status_code: int = 200, response_time_ms: int = None) -> bool:
        """Save fetched page to database"""
        try:
            md5_hash = hashlib.md5(html.encode()).hexdigest()
            content_length = len(html.encode())
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO pages
                (url, html, status_code, content_length, md5_hash, response_time_ms)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (url, html, status_code, content_length, md5_hash, response_time_ms))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            logger.error(f"Error saving page {url}: {e}")
            return False
    
    def page_exists(self, url: str) -> bool:
        """Check if page already fetched"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM pages WHERE url = ?', (url,))
            result = cursor.fetchone() is not None
            conn.close()
            return result
        except Exception as e:
            logger.warning(f"Error checking page existence: {e}")
            return False
    
    def get_page_html(self, url: str) -> Optional[str]:
        """Retrieve cached HTML"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT html FROM pages WHERE url = ?', (url,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            logger.warning(f"Error retrieving page: {e}")
            return None
    
    def log_error(self, url: str, error_type: str, error_message: str = None, status_code: int = None, attempt_count: int = 1) -> bool:
        """Log fetch errors"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO error_log
                (url, error_type, error_message, status_code, attempt_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (url, error_type, error_message, status_code, attempt_count))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error logging error: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM pages')
            total_pages = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM error_log')
            total_errors = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(content_length) FROM pages')
            total_size = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_pages': total_pages,
                'total_errors': total_errors,
                'total_size_mb': round(total_size / 1024 / 1024, 2)
            }
        
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'total_pages': 0, 'total_errors': 0, 'total_size_mb': 0}


class ProductionCrawler:
    """Production-ready web crawler"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    ]
    
    def __init__(
        self,
        start_url: str,
        max_pages: int = 50,
        rate_limit_per_sec: float = 2.0,
        timeout_seconds: int = 30,
        max_retries: int = 3,
        use_db: bool = True,
        db_path: str = 'crawler.db'
    ):
        self.start_url = start_url
        self.max_pages = max_pages
        self.rate_limit_per_sec = rate_limit_per_sec
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        
        self.domain = urlparse(start_url).netloc
        self.visited: Set[str] = set()
        self.queue = [start_url]
        self.db = CrawlerDatabase(db_path) if use_db else None
        
        self.stats = {
            'total_fetched': 0,
            'total_errors': 0,
            'total_retries': 0,
            'http_errors': {},
        }
    
    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Fetch URL with exponential backoff retry logic"""
        
        for attempt in range(self.max_retries):
            try:
                headers = {
                    'User-Agent': random.choice(self.USER_AGENTS),
                    'Accept': 'text/html,application/xhtml+xml',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                }
                
                timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
                
                async with session.get(
                    url,
                    headers=headers,
                    timeout=timeout,
                    ssl=True,
                    allow_redirects=True
                ) as response:
                    
                    if response.status == 200:
                        html = await response.text()
                        logger.info(f"✅ {url} ({len(html)} bytes)")
                        self.stats['total_fetched'] += 1
                        if self.db:
                            self.db.save_page(url, html, 200)
                        return html
                    
                    elif response.status == 429:
                        retry_after = int(response.headers.get('Retry-After', 2**attempt))
                        logger.warning(f"⏱️  Rate limited, waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue
                    
                    elif response.status >= 500:
                        logger.warning(f"🔄 Server error {response.status}, retry {attempt+1}/{self.max_retries}")
                        await asyncio.sleep(2**attempt)
                        continue
                    
                    elif response.status in [301, 302, 303, 307, 308]:
                        html = await response.text()
                        logger.info(f"↩️  Redirect {response.status}: {url}")
                        self.stats['total_fetched'] += 1
                        if self.db:
                            self.db.save_page(url, html, response.status)
                        return html
                    
                    elif response.status == 404:
                        logger.debug(f"❌ 404 Not Found: {url}")
                        self.stats['http_errors'][404] = self.stats['http_errors'].get(404, 0) + 1
                        if self.db:
                            self.db.log_error(url, 'HTTP_404', status_code=404)
                        return None
                    
                    elif response.status == 403:
                        logger.error(f"🚫 403 Forbidden: {url}")
                        self.stats['http_errors'][403] = self.stats['http_errors'].get(403, 0) + 1
                        if self.db:
                            self.db.log_error(url, 'HTTP_403_FORBIDDEN', status_code=403)
                        return None
                    
                    else:
                        logger.warning(f"⚠️  HTTP {response.status}: {url}")
                        self.stats['http_errors'][response.status] = self.stats['http_errors'].get(response.status, 0) + 1
                        return None
            
            except asyncio.TimeoutError:
                logger.warning(f"⏳ Timeout attempt {attempt+1}/{self.max_retries}: {url}")
                self.stats['total_retries'] += 1
                if self.db:
                    self.db.log_error(url, 'TIMEOUT', attempt_count=attempt+1)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
            
            except aiohttp.ClientSSLError as e:
                logger.error(f"🔒 SSL Error: {url} - {e}")
                self.stats['total_errors'] += 1
                if self.db:
                    self.db.log_error(url, 'SSL_ERROR', str(e))
                return None
            
            except aiohttp.ClientConnectorError as e:
                logger.warning(f"🌐 Connection error attempt {attempt+1}: {type(e).__name__}")
                self.stats['total_retries'] += 1
                if self.db:
                    self.db.log_error(url, 'CONNECTION_ERROR', str(e), attempt_count=attempt+1)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
            
            except aiohttp.ClientError as e:
                logger.error(f"❌ Client error: {type(e).__name__}: {e}")
                self.stats['total_errors'] += 1
                if self.db:
                    self.db.log_error(url, 'CLIENT_ERROR', str(e))
                return None
            
            except Exception as e:
                logger.error(f"💥 Unexpected error: {type(e).__name__}: {e}")
                self.stats['total_errors'] += 1
                if self.db:
                    self.db.log_error(url, 'UNEXPECTED_ERROR', str(e))
                raise
        
        logger.error(f"❌ Failed after {self.max_retries} retries: {url}")
        self.stats['total_errors'] += 1
        if self.db:
            self.db.log_error(url, 'MAX_RETRIES_EXCEEDED')
        return None
    
    async def parse_links(self, html: str, base_url: str) -> list:
        """Parse links from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            for a in soup.find_all('a', href=True):
                href = a.get('href', '').strip()
                if not href:
                    continue
                
                full_url = urljoin(base_url, href)
                normalized_url = URLNormalizer.normalize(full_url)
                
                if URLNormalizer.validate(normalized_url, self.domain):
                    links.append(normalized_url)
            
            logger.debug(f"Found {len(links)} links in {base_url}")
            return links
        
        except Exception as e:
            logger.error(f"Parse error in {base_url}: {type(e).__name__}: {e}")
            return []
    
    async def run(self) -> Dict:
        """Main crawl loop"""
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        connector = aiohttp.TCPConnector(
            limit_per_host=2,
            limit=10,
            ttl_dns_cache=300
        )
        
        start_time = datetime.now()
        logger.info(f"Starting crawl: {self.start_url}")
        logger.info(f"Max pages: {self.max_pages}, Rate limit: {self.rate_limit_per_sec} req/s")
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            
            while self.queue and len(self.visited) < self.max_pages:
                url = self.queue.pop(0)
                normalized_url = URLNormalizer.normalize(url)
                
                if normalized_url in self.visited:
                    continue
                
                self.visited.add(normalized_url)
                logger.info(f"[{len(self.visited)}/{self.max_pages}] {url}")
                
                await asyncio.sleep(1.0 / self.rate_limit_per_sec)
                
                html = await self.fetch(session, normalized_url)
                
                if html:
                    links = await self.parse_links(html, normalized_url)
                    
                    for link in links:
                        if link not in self.visited and link not in self.queue:
                            self.queue.append(link)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Crawl complete!")
        logger.info(f"{'='*60}")
        logger.info(f"Total pages visited: {len(self.visited)}")
        logger.info(f"Total pages fetched: {self.stats['total_fetched']}")
        logger.info(f"Total errors: {self.stats['total_errors']}")
        logger.info(f"Total retries: {self.stats['total_retries']}")
        logger.info(f"HTTP error codes: {self.stats['http_errors']}")
        logger.info(f"Time elapsed: {elapsed:.1f}s")
        logger.info(f"Rate: {len(self.visited)/elapsed:.1f} pages/sec")
        
        if self.db:
            db_stats = self.db.get_stats()
            logger.info(f"Database: {db_stats['total_pages']} pages, {db_stats['total_size_mb']}MB")
        
        logger.info(f"{'='*60}\n")
        
        return {
            'total_visited': len(self.visited),
            'total_fetched': self.stats['total_fetched'],
            'total_errors': self.stats['total_errors'],
            'elapsed_seconds': elapsed,
            'rate_per_sec': round(len(self.visited)/elapsed, 2),
            'stats': self.stats
        }


async def main():
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    crawler = ProductionCrawler(
        start_url=os.getenv('START_URL', 'https://example.com'),
        max_pages=int(os.getenv('MAX_PAGES', 50)),
        rate_limit_per_sec=float(os.getenv('RATE_LIMIT_PER_SEC', 2.0)),
        timeout_seconds=int(os.getenv('TIMEOUT_SECONDS', 30)),
        max_retries=int(os.getenv('MAX_RETRIES', 3)),
        use_db=os.getenv('USE_DB', 'true').lower() == 'true',
        db_path=os.getenv('DB_FILE', 'crawler.db')
    )
    
    result = await crawler.run()
    print(f"\n🎉 Result: {result}")


if __name__ == '__main__':
    asyncio.run(main())
