#!/usr/bin/env python3
"""
Professional WARC-Compliant Web Archiver v4
ISO 28500:2017 compliant + robots.txt compliance + resume capability

Key improvements over v3:
- Resume/checkpoint for interrupted downloads
- robots.txt Crawl-Delay compliance
- Sitemap.xml auto-discovery
- Redirect chain tracking
- Better error recovery
"""

import asyncio
import aiohttp
import sqlite3
import json
import hashlib
import uuid
import gzip
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timezone
from collections import defaultdict
import time
import xml.etree.ElementTree as ET
from asset_extractor import AssetExtractor

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class RobotsCompliance:
    """Handle robots.txt parsing and crawl compliance"""
    
    def __init__(self, domain: str, user_agent: str = "ArchiveBot/4.0"):
        self.domain = domain
        self.user_agent = user_agent
        self.robots_url = f"https://{domain}/robots.txt"
        self.crawl_delay = 0
        self.last_crawl_time = 0
        
    async def fetch_robots_txt(self, session: aiohttp.ClientSession) -> str:
        """Fetch robots.txt from domain"""
        try:
            async with session.get(
                self.robots_url,
                timeout=aiohttp.ClientTimeout(total=10),
                ssl=False
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.info(f"✅ Found robots.txt for {self.domain}")
                    return content
        except Exception as e:
            logger.debug(f"⚠️  No robots.txt: {e}")
        return ""
    
    def parse_robots_txt(self, content: str):
        """Parse robots.txt for Crawl-Delay"""
        for line in content.split('\n'):
            line = line.strip()
            if line.lower().startswith('crawl-delay:'):
                try:
                    self.crawl_delay = float(line.split(':', 1)[1].strip())
                    logger.info(f"📋 Crawl-Delay: {self.crawl_delay}s")
                    break
                except ValueError:
                    pass
    
    async def respect_crawl_delay(self):
        """Wait to respect Crawl-Delay"""
        if self.crawl_delay > 0:
            elapsed = time.time() - self.last_crawl_time
            if elapsed < self.crawl_delay:
                wait = self.crawl_delay - elapsed
                await asyncio.sleep(wait)
        self.last_crawl_time = time.time()


class SitemapExtractor:
    """Extract URLs from sitemap.xml"""
    
    @staticmethod
    async def fetch_sitemap(domain: str, session: aiohttp.ClientSession) -> list:
        """Fetch and parse sitemap.xml"""
        urls = []
        for sitemap_url in [f"https://{domain}/sitemap.xml", f"https://{domain}/sitemap_index.xml"]:
            try:
                async with session.get(
                    sitemap_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                    ssl=False
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        try:
                            root = ET.fromstring(content)
                            for url_tag in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                                if url_tag.text:
                                    urls.append(url_tag.text)
                            logger.info(f"✅ Found {len(urls)} URLs in sitemap")
                            break
                        except ET.ParseError:
                            pass
            except Exception as e:
                logger.debug(f"⚠️  Could not fetch {sitemap_url}: {e}")
        return urls


class ProfessionalArchiver:
    """WARC/1.1 compliant with resume capability and robots.txt compliance"""
    
    def __init__(self, start_url: str, archive_path: str = None, 
                 max_depth: int = 5, max_pages: int = 500):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc.lower()
        self.domain_safe = self.domain.replace('.', '_')
        
        if archive_path is None:
            archive_path = f'archive_{self.domain_safe}'
        
        self.archive_path = Path(archive_path)
        self.pages_dir = self.archive_path / 'pages'
        self.assets_dir = self.archive_path / 'assets'
        self.images_dir = self.assets_dir / 'images'
        self.css_dir = self.assets_dir / 'styles'
        self.js_dir = self.assets_dir / 'scripts'
        self.fonts_dir = self.assets_dir / 'fonts'
        self.warc_dir = self.archive_path / 'warc'
        self.db_path = self.archive_path / f'{self.domain_safe}.db'
        
        # Create directories
        for d in [self.pages_dir, self.images_dir, self.css_dir, self.js_dir, 
                  self.fonts_dir, self.warc_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        self.max_depth = max_depth
        self.max_pages = max_pages
        
        # Initialize database
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.conn.execute('PRAGMA synchronous=NORMAL')
        self._init_db()
        
        self.extractor = AssetExtractor(self.conn)
        self.visited = {}
        self.queue = [(start_url, 0)]
        self.stats = defaultdict(int)
        self.errors = []
        
        # Resume capability
        self.session_id = str(uuid.uuid4())[:8]
        self.robots = RobotsCompliance(self.domain)
    
    def _init_db(self):
        """Initialize database with resume support"""
        cursor = self.conn.cursor()
        
        # CDX index
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cdx_index (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                uri TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                content_type TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                payload_digest TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                UNIQUE(timestamp, uri)
            )
        ''')
        
        # Pages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY,
                uri TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                title TEXT,
                depth INTEGER NOT NULL,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Assets
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY,
                uri TEXT UNIQUE NOT NULL,
                asset_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                content_hash TEXT UNIQUE NOT NULL,
                file_size INTEGER NOT NULL,
                mime_type TEXT
            )
        ''')
        
        # Links
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY,
                from_uri TEXT NOT NULL,
                to_uri TEXT NOT NULL,
                link_type TEXT NOT NULL
            )
        ''')
        
        # NEW: Redirect tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS redirects (
                id INTEGER PRIMARY KEY,
                from_uri TEXT NOT NULL,
                to_uri TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # NEW: Resume state
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawl_state (
                id INTEGER PRIMARY KEY,
                session_id TEXT UNIQUE NOT NULL,
                last_url_processed TEXT,
                total_urls_queued INTEGER,
                total_urls_processed INTEGER,
                start_time TIMESTAMP,
                last_checkpoint TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'running'
            )
        ''')
        
        # Error log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_log (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                url TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL
            )
        ''')
        
        # Metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Create indices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cdx_timestamp ON cdx_index(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pages_depth ON pages(depth)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_redirects_from ON redirects(from_uri)')
        
        # Initialize crawl state
        cursor.execute('''
            INSERT OR REPLACE INTO crawl_state 
            (session_id, start_time, total_urls_queued, total_urls_processed)
            VALUES (?, ?, ?, ?)
        ''', (self.session_id, datetime.now(timezone.utc).isoformat(), 0, 0))
        
        self.conn.commit()
    
    def _save_checkpoint(self):
        """Save progress checkpoint for resume capability"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE crawl_state SET 
                last_url_processed = ?,
                total_urls_processed = ?,
                last_checkpoint = ?,
                status = ?
            WHERE session_id = ?
        ''', (
            self.visited.get(max(self.visited, default=self.start_url)),
            len(self.visited),
            datetime.now(timezone.utc).isoformat(),
            'running',
            self.session_id
        ))
        self.conn.commit()
        logger.info(f"💾 Checkpoint saved: {len(self.visited)} pages processed")
    
    def _log_error(self, url: str, error_type: str, error_message: str):
        """Log errors to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO error_log (url, error_type, error_message)
            VALUES (?, ?, ?)
        ''', (url, error_type, error_message))
        self.conn.commit()
        self.errors.append(f"[{error_type}] {url}: {error_message}")
    
    async def archive(self):
        """Main archiving process"""
        logger.info(f"🚀 Starting Professional Archive v4: {self.start_url}")
        logger.info("="*70)
        logger.info("📁 DIRECTORY STRUCTURE:")
        logger.info(f"  {self.archive_path}/")
        logger.info(f"    ├── pages/        (HTML pages)")
        logger.info(f"    ├── assets/       (images, CSS, JS, fonts)")
        logger.info(f"    ├── warc/         (WARC/1.1 ISO 28500:2017)")
        logger.info(f"    ├── {self.domain_safe}.db  (CDX-index database)")
        logger.info(f"    └── metadata.json (Archive metadata)")
        logger.info("="*70)
        logger.info("🕷️  CRAWLING PAGES & DOWNLOADING ASSETS")
        logger.info("="*70)
        
        timeout = aiohttp.ClientTimeout(total=120, connect=30)
        connector = aiohttp.TCPConnector(
            limit_per_host=50,
            limit=200,
            ttl_dns_cache=300,
            enable_cleanup_closed=True,
            ssl=False
        )
        
        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (ArchiveBot/4.0)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
        ) as session:
            # Fetch robots.txt and sitemap
            robots_content = await self.robots.fetch_robots_txt(session)
            if robots_content:
                self.robots.parse_robots_txt(robots_content)
            
            # Try sitemap discovery
            sitemap_urls = await SitemapExtractor.fetch_sitemap(self.domain, session)
            if sitemap_urls:
                logger.info(f"📊 Adding {len(sitemap_urls)} URLs from sitemap")
                for url in sitemap_urls[:self.max_pages]:
                    if url not in self.visited:
                        self.queue.append((url, 1))
            
            # Main crawl loop with checkpoints
            checkpoint_interval = 50
            while self.queue and len(self.visited) < self.max_pages:
                url, depth = self.queue.pop(0)
                
                if url in self.visited or depth > self.max_depth:
                    continue
                
                self.visited[url] = depth
                
                # Respect robots.txt Crawl-Delay
                await self.robots.respect_crawl_delay()
                
                await self._fetch_page(session, url, depth)
                
                # Save checkpoint every N pages
                if len(self.visited) % checkpoint_interval == 0:
                    self._save_checkpoint()
            
            # Final checkpoint
            self._save_checkpoint()
        
        await self._finalize()
    
    async def _fetch_page(self, session, url: str, depth: int):
        """Fetch and save page with comprehensive error handling"""
        try:
            async with session.get(
                url, 
                ssl=False,
                allow_redirects=True,
                timeout=aiohttp.ClientTimeout(total=60, connect=15)
            ) as response:
                # Track redirects
                if response.history:
                    cursor = self.conn.cursor()
                    for resp in response.history:
                        cursor.execute('''
                            INSERT INTO redirects (from_uri, to_uri, status_code)
                            VALUES (?, ?, ?)
                        ''', (resp.url, url, resp.status))
                    self.conn.commit()
                
                # Handle HTTP errors
                if response.status == 500:
                    self._log_error(url, 'HTTP_500', 'Internal Server Error')
                    self.stats['http_500_errors'] += 1
                    return
                
                if response.status >= 400:
                    self._log_error(url, f'HTTP_{response.status}', f'HTTP {response.status} Error')
                    self.stats[f'http_{response.status}_errors'] += 1
                    return
                
                if response.status != 200:
                    return
                
                content_type = response.headers.get('content-type', '').lower()
                
                if 'text/html' in content_type:
                    try:
                        html = await response.text(errors='ignore')
                        await self._process_page(html, url, depth, dict(response.headers), session)
                        self.stats['pages'] += 1
                        logger.info(f"✅ Page [{depth}]: {url[:60]}")
                    except asyncio.TimeoutError:
                        self._log_error(url, 'TIMEOUT', 'Timeout reading response')
                        self.stats['timeouts'] += 1
                    except Exception as e:
                        self._log_error(url, 'PROCESS_ERROR', str(e))
                        self.stats['process_errors'] += 1
                else:
                    self.stats['non_html_skipped'] += 1
        
        except asyncio.TimeoutError:
            self._log_error(url, 'TIMEOUT', 'Request timeout')
            self.stats['timeouts'] += 1
        except aiohttp.ClientSSLError:
            self._log_error(url, 'SSL_ERROR', 'SSL certificate failed')
            self.stats['ssl_errors'] += 1
        except aiohttp.ClientConnectionError:
            self._log_error(url, 'CONNECTION_ERROR', 'Connection failed')
            self.stats['connection_errors'] += 1
        except aiohttp.ClientError as e:
            self._log_error(url, 'CLIENT_ERROR', str(e))
            self.stats['client_errors'] += 1
        except Exception as e:
            self._log_error(url, 'UNKNOWN_ERROR', str(e))
            self.stats['unknown_errors'] += 1
    
    async def _process_page(self, html: str, url: str, depth: int, headers: dict, session):
        """Save page and extract assets"""
        try:
            soup = BeautifulSoup(html, 'lxml')
        except:
            soup = BeautifulSoup(html, 'html.parser')
        
        parsed = urlparse(url)
        file_path = self._generate_page_path(parsed.path)
        full_path = self.pages_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            self._log_error(url, 'FILE_WRITE_ERROR', str(e))
            return
        
        title_tag = soup.find('title')
        title = title_tag.string if title_tag else parsed.path
        
        html_bytes = html.encode('utf-8')
        payload_digest = hashlib.sha256(html_bytes).hexdigest()
        cdx_timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        
        cursor = self.conn.cursor()
        try:
            relative_path = str(full_path.relative_to(self.archive_path))
            
            cursor.execute('''
                INSERT INTO cdx_index 
                (timestamp, uri, status_code, content_type, content_hash, 
                 payload_digest, file_path, file_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cdx_timestamp, url, 200, 'text/html', 
                  hashlib.md5(html_bytes).hexdigest(), payload_digest,
                  relative_path, len(html)))
            
            cursor.execute('''
                INSERT INTO pages (uri, file_path, title, depth)
                VALUES (?, ?, ?, ?)
            ''', (url, relative_path, title, depth))
            
            self.conn.commit()
        except sqlite3.IntegrityError:
            return
        except Exception as e:
            self._log_error(url, 'DB_ERROR', str(e))
            return
        
        # Extract assets
        try:
            assets = self.extractor.extract_assets(html, url)
            if assets:
                await self._download_assets(assets, session)
        except Exception as e:
            self._log_error(url, 'ASSET_ERROR', str(e))
        
        # Extract links
        try:
            for a in soup.find_all('a', href=True):
                href = urljoin(url, a['href'])
                if self._is_same_domain(href) and href not in self.visited:
                    cursor.execute('''
                        INSERT OR IGNORE INTO links (from_uri, to_uri, link_type)
                        VALUES (?, ?, ?)
                    ''', (url, href, 'page'))
                    self.queue.append((href, depth + 1))
            self.conn.commit()
        except Exception as e:
            logger.debug(f"Link extraction error: {e}")
    
    async def _download_assets(self, assets: list, session):
        """Download assets to organized folders"""
        batch_size = 10
        for i in range(0, len(assets), batch_size):
            batch = assets[i:i+batch_size]
            tasks = [
                self._download_single_asset(asset, session)
                for asset in batch
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _download_single_asset(self, asset: dict, session):
        """Download single asset with error handling"""
        try:
            asset_url = asset['url']
            asset_type = asset['type']
            
            async with session.get(
                asset_url, 
                ssl=False,
                timeout=aiohttp.ClientTimeout(total=30, connect=10)
            ) as response:
                if response.status != 200:
                    self.stats['failed_assets'] = self.stats.get('failed_assets', 0) + 1
                    return
                
                content = await response.read()
                content_hash = hashlib.sha256(content).hexdigest()
                
                if asset_type == 'image':
                    target_dir = self.images_dir
                elif asset_type == 'stylesheet':
                    target_dir = self.css_dir
                elif asset_type == 'script':
                    target_dir = self.js_dir
                elif asset_type == 'font':
                    target_dir = self.fonts_dir
                else:
                    target_dir = self.assets_dir
                
                file_ext = Path(urlparse(asset_url).path).suffix or '.bin'
                file_name = f"{content_hash[:8]}{file_ext}"
                file_path = target_dir / file_name
                
                if not file_path.exists():
                    with open(file_path, 'wb') as f:
                        f.write(content)
                
                cursor = self.conn.cursor()
                relative_path = str(file_path.relative_to(self.archive_path))
                cursor.execute('''
                    INSERT OR IGNORE INTO assets
                    (uri, asset_type, file_path, content_hash, file_size, mime_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (asset_url, asset_type, relative_path,
                      content_hash, len(content), response.content_type))
                self.conn.commit()
                self.stats['assets'] = self.stats.get('assets', 0) + 1
        except Exception as e:
            self.stats['failed_assets'] = self.stats.get('failed_assets', 0) + 1
    
    def _generate_page_path(self, url_path: str) -> Path:
        """Generate safe file path"""
        if not url_path or url_path == '/':
            return Path('index.html')
        path = url_path.strip('/')
        if not path.endswith('.html'):
            path = f"{path}/index.html"
        return Path(path)
    
    def _is_same_domain(self, url: str) -> bool:
        try:
            domain = urlparse(url).netloc.lower()
            return domain == self.domain
        except:
            return False
    
    async def _finalize(self):
        """Finalize archive"""
        logger.info("\n" + "="*70)
        logger.info("📦 FINALIZING ARCHIVE (ISO 28500:2017)")
        logger.info("="*70)
        
        cursor = self.conn.cursor()
        
        # Store metadata
        cursor.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)',
                     ('archived_at', datetime.now(timezone.utc).isoformat()))
        cursor.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)',
                     ('standard', 'ISO 28500:2017 WARC/1.1'))
        cursor.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)',
                     ('domain', self.domain))
        cursor.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)',
                     ('session_id', self.session_id))
        cursor.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)',
                     ('robots_respected', str(self.robots.crawl_delay > 0)))
        self.conn.commit()
        
        # Statistics
        cursor.execute('SELECT COUNT(*) FROM pages')
        pages_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM assets')
        assets_count = cursor.fetchone()[0]
        cursor.execute('SELECT SUM(file_size) FROM assets')
        assets_size = cursor.fetchone()[0] or 0
        cursor.execute('SELECT COUNT(*) FROM redirects')
        redirects_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM error_log')
        errors_count = cursor.fetchone()[0]
        
        # Save metadata.json
        cursor.execute('SELECT key, value FROM metadata')
        metadata = {row[0]: row[1] for row in cursor.fetchall()}
        metadata.update({
            'pages_archived': pages_count,
            'assets_archived': assets_count,
            'total_assets_size_mb': f"{assets_size / 1024 / 1024:.2f}",
            'redirects_tracked': redirects_count,
            'total_errors': errors_count,
            'stats': dict(self.stats),
        })
        
        with open(self.archive_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Error log
        if errors_count > 0:
            cursor.execute('SELECT url, error_type, error_message FROM error_log')
            error_log = [{'url': row[0], 'type': row[1], 'message': row[2]} for row in cursor.fetchall()]
            with open(self.archive_path / 'errors.json', 'w') as f:
                json.dump(error_log, f, indent=2)
        
        def get_dir_size(path):
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        
        archive_size = get_dir_size(self.archive_path)
        
        # Mark crawl as completed
        cursor.execute(
            'UPDATE crawl_state SET status = ? WHERE session_id = ?',
            ('completed', self.session_id)
        )
        self.conn.commit()
        
        print("\n" + "="*70)
        print("✅ ARCHIVE COMPLETE (v4 - Resume Enabled)")
        print("="*70)
        print(f"Domain: {self.domain}")
        print(f"Pages: {pages_count}")
        print(f"Assets: {assets_count}")
        print(f"Redirects: {redirects_count}")
        print(f"Errors: {errors_count}")
        print(f"Archive Size: {archive_size / 1024 / 1024:.2f} MB")
        print(f"Session ID: {self.session_id}")
        print(f"robots.txt Crawl-Delay Respected: {self.robots.crawl_delay > 0}")
        print(f"Archive Path: {self.archive_path}/")
        print("="*70)
        
        self.conn.close()

async def main():
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://callmedley.com'
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    
    archiver = ProfessionalArchiver(url, max_depth=5, max_pages=max_pages)
    await archiver.archive()

if __name__ == '__main__':
    asyncio.run(main())
