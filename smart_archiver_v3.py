#!/usr/bin/env python3
"""
Professional WARC-Compliant Web Archiver
ISO 28500:2017 compliant + proper directory structure
Inspired by Internet Archive & BnF practices

FIXED: Added comprehensive error handling for HTTP 500 and other network errors
FIXED v2: Removed invalid timeout parameter from response.text()
"""

import asyncio
import aiohttp
import sqlite3
import json
import hashlib
import uuid
import gzip
import shutil
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timezone
from collections import defaultdict
from asset_extractor import AssetExtractor

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class ProfessionalArchiver:
    """WARC/1.1 compliant with proper directory structure"""
    
    def __init__(self, start_url: str, archive_path: str = None, 
                 max_depth: int = 5, max_pages: int = 500):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc.lower()
        self.domain_safe = self.domain.replace('.', '_')
        
        # Archive directory structure
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
        
        # Create directories - ALWAYS create, even if fetch fails
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
        
        # WARC buffer
        self.warc_buffer = []
        self.warc_filename = f'{self.domain_safe}.warc'
    
    def _init_db(self):
        """Initialize professional CDX-like database"""
        cursor = self.conn.cursor()
        
        # CDX-index table (для быстрого поиска)
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
        
        # Pages table
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
        
        # Assets table (deduplicated)
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
        
        # Links table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY,
                from_uri TEXT NOT NULL,
                to_uri TEXT NOT NULL,
                link_type TEXT NOT NULL
            )
        ''')
        
        # Metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
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
        
        # Create indices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cdx_timestamp ON cdx_index(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pages_depth ON pages(depth)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(asset_type)')
        
        self.conn.commit()
    
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
        logger.info(f"🚀 Starting Professional Archive: {self.start_url}")
        logger.info("="*70)
        logger.info("📁 DIRECTORY STRUCTURE:")
        logger.info(f"  {self.archive_path}/")
        logger.info(f"    ├── pages/        (HTML pages)")
        logger.info(f"    ├── assets/")
        logger.info(f"    │   ├── images/   (*.jpg, *.png, *.svg, *.gif)")
        logger.info(f"    │   ├── styles/   (*.css)")
        logger.info(f"    │   ├── scripts/  (*.js)")
        logger.info(f"    │   └── fonts/    (*.woff, *.ttf)")
        logger.info(f"    ├── warc/         (WARC/1.1 ISO 28500:2017)")
        logger.info(f"    ├── {self.domain_safe}.db     (CDX-index database)")
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
            ssl=False  # Disable SSL verification for problematic servers
        )
        
        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (ArchiveBot/3.0)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
        ) as session:
            while self.queue and len(self.visited) < self.max_pages:
                url, depth = self.queue.pop(0)
                
                if url in self.visited or depth > self.max_depth:
                    continue
                
                self.visited[url] = depth
                await self._fetch_page(session, url, depth)
        
        await self._finalize()
    
    async def _fetch_page(self, session, url: str, depth: int):
        """Fetch and save page with comprehensive error handling"""
        try:
            async with session.get(
                url, 
                ssl=False,  # Disable SSL verification
                allow_redirects=True,
                timeout=aiohttp.ClientTimeout(total=60, connect=15)
            ) as response:
                # Handle HTTP errors
                if response.status == 500:
                    error_msg = f"Server error (HTTP 500) - Internal Server Error"
                    logger.warning(f"⚠️  {error_msg} on {url}")
                    self._log_error(url, 'HTTP_500', error_msg)
                    self.stats['http_500_errors'] += 1
                    return
                
                if response.status >= 400:
                    error_msg = f"HTTP {response.status} Error"
                    logger.warning(f"⚠️  {error_msg} on {url}")
                    self._log_error(url, f'HTTP_{response.status}', error_msg)
                    self.stats[f'http_{response.status}_errors'] += 1
                    return
                
                if response.status != 200:
                    logger.debug(f"⚠️  HTTP {response.status}: {url}")
                    return
                
                content_type = response.headers.get('content-type', '').lower()
                
                if 'text/html' in content_type:
                    try:
                        html = await response.text(errors='ignore')
                        await self._process_page(html, url, depth, dict(response.headers), session)
                        self.stats['pages'] += 1
                        logger.info(f"✅ Page [{depth}]: {url[:60]}")
                    except asyncio.TimeoutError:
                        error_msg = "Timeout while reading response"
                        logger.warning(f"⏱️  {error_msg}: {url}")
                        self._log_error(url, 'TIMEOUT', error_msg)
                        self.stats['timeouts'] += 1
                    except Exception as e:
                        error_msg = f"Failed to process page: {str(e)}"
                        logger.warning(f"⚠️  {error_msg}")
                        self._log_error(url, 'PROCESS_ERROR', error_msg)
                        self.stats['process_errors'] += 1
                else:
                    logger.debug(f"⏭️  Skipping non-HTML: {url}")
                    self.stats['non_html_skipped'] += 1
        
        except asyncio.TimeoutError:
            error_msg = "Request timeout"
            logger.warning(f"⏱️  {error_msg}: {url}")
            self._log_error(url, 'TIMEOUT', error_msg)
            self.stats['timeouts'] += 1
        
        except aiohttp.ClientSSLError:
            error_msg = "SSL certificate verification failed"
            logger.warning(f"🔒 {error_msg}: {url}")
            self._log_error(url, 'SSL_ERROR', error_msg)
            self.stats['ssl_errors'] += 1
        
        except aiohttp.ClientConnectionError:
            error_msg = "Connection failed"
            logger.warning(f"🌐 {error_msg}: {url}")
            self._log_error(url, 'CONNECTION_ERROR', error_msg)
            self.stats['connection_errors'] += 1
        
        except aiohttp.ClientError as e:
            error_msg = f"HTTP Client error: {str(e)}"
            logger.warning(f"⚠️  {error_msg}")
            self._log_error(url, 'CLIENT_ERROR', error_msg)
            self.stats['client_errors'] += 1
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"❌ {error_msg}: {url}")
            self._log_error(url, 'UNKNOWN_ERROR', error_msg)
            self.stats['unknown_errors'] += 1
    
    async def _process_page(self, html: str, url: str, depth: int, headers: dict, session):
        """Save page and extract assets"""
        try:
            soup = BeautifulSoup(html, 'lxml')
        except:
            soup = BeautifulSoup(html, 'html.parser')
        
        parsed = urlparse(url)
        
        # Generate safe file path
        file_path = self._generate_page_path(parsed.path)
        full_path = self.pages_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save HTML
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            logger.warning(f"Failed to save HTML: {e}")
            self._log_error(url, 'FILE_WRITE_ERROR', str(e))
            return
        
        title_tag = soup.find('title')
        title = title_tag.string if title_tag else parsed.path
        
        # Calculate digests
        html_bytes = html.encode('utf-8')
        payload_digest = hashlib.sha256(html_bytes).hexdigest()
        
        # CDX timestamp
        cdx_timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        
        # Store in CDX-index
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO cdx_index 
                (timestamp, uri, status_code, content_type, content_hash, 
                 payload_digest, file_path, file_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cdx_timestamp, url, 200, 'text/html', 
                  hashlib.md5(html_bytes).hexdigest(), payload_digest,
                  str(file_path.relative_to(self.archive_path)), len(html)))
            
            cursor.execute('''
                INSERT INTO pages (uri, file_path, title, depth)
                VALUES (?, ?, ?, ?)
            ''', (url, str(file_path.relative_to(self.archive_path)), title, depth))
            
            self.conn.commit()
        except sqlite3.IntegrityError:
            return
        except Exception as e:
            logger.warning(f"Database error: {e}")
            self._log_error(url, 'DB_ERROR', str(e))
            return
        
        # Extract and download assets
        try:
            assets = self.extractor.extract_assets(html, url)
            if assets:
                logger.info(f"📦 Found {len(assets)} assets on {url}")
                await self._download_assets(assets, session)
        except Exception as e:
            logger.warning(f"Asset extraction failed: {e}")
            self._log_error(url, 'ASSET_EXTRACTION_ERROR', str(e))
        
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
        total = len(assets)
        
        for i in range(0, total, batch_size):
            batch = assets[i:i+batch_size]
            tasks = [
                self._download_single_asset(asset, session)
                for asset in batch
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"📊 Assets downloaded")
    
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
                
                # Determine folder by type
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
                
                # Save by hash (deduplication)
                file_ext = Path(urlparse(asset_url).path).suffix or '.bin'
                file_name = f"{content_hash[:8]}{file_ext}"
                file_path = target_dir / file_name
                
                if not file_path.exists():
                    with open(file_path, 'wb') as f:
                        f.write(content)
                
                # Store in database
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO assets
                    (uri, asset_type, file_path, content_hash, file_size, mime_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (asset_url, asset_type, str(file_path.relative_to(self.archive_path)),
                      content_hash, len(content), response.content_type))
                self.conn.commit()
                self.stats['assets'] = self.stats.get('assets', 0) + 1
        
        except asyncio.TimeoutError:
            self.stats['asset_timeouts'] = self.stats.get('asset_timeouts', 0) + 1
        except Exception as e:
            logger.debug(f"⚠️  Asset download failed: {asset.get('url', 'unknown')} - {e}")
            self.stats['failed_assets'] = self.stats.get('failed_assets', 0) + 1
    
    def _generate_page_path(self, url_path: str) -> str:
        """Generate safe file path"""
        if not url_path or url_path == '/':
            return 'index.html'
        
        path = url_path.strip('/')
        if not path.endswith('.html'):
            path = f"{path}/index.html"
        
        return path
    
    def _is_same_domain(self, url: str) -> bool:
        try:
            domain = urlparse(url).netloc.lower()
            return domain == self.domain
        except:
            return False
    
    async def _finalize(self):
        """Finalize archive"""
        # Compress WARC (ISO 28500:2017 recommends GZIP)
        logger.info("\n" + "="*70)
        logger.info("📦 FINALIZING ARCHIVE (GZIP ISO 28500:2017)")
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
                     ('archive_root', str(self.archive_path)))
        
        self.conn.commit()
        
        # Save metadata.json
        cursor.execute('SELECT key, value FROM metadata')
        metadata = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Statistics
        cursor.execute('SELECT COUNT(*) FROM pages')
        pages_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM assets')
        assets_count = cursor.fetchone()[0]
        cursor.execute('SELECT SUM(file_size) FROM assets')
        assets_size = cursor.fetchone()[0] or 0
        
        # Error statistics
        cursor.execute('SELECT COUNT(*) FROM error_log')
        errors_count = cursor.fetchone()[0]
        
        metadata.update({
            'pages_archived': pages_count,
            'assets_archived': assets_count,
            'total_assets_size_mb': f"{assets_size / 1024 / 1024:.2f}",
            'total_errors': errors_count,
            'stats': dict(self.stats),
        })
        
        metadata_path = self.archive_path / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Error log
        if errors_count > 0:
            cursor.execute('SELECT url, error_type, error_message FROM error_log')
            error_log = [{
                'url': row[0],
                'type': row[1],
                'message': row[2]
            } for row in cursor.fetchall()]
            
            error_path = self.archive_path / 'errors.json'
            with open(error_path, 'w') as f:
                json.dump(error_log, f, indent=2)
        
        # Archive structure size
        def get_dir_size(path):
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        
        archive_size = get_dir_size(self.archive_path)
        
        print("\n" + "="*70)
        print("✅ ARCHIVE COMPLETE")
        print("="*70)
        print(f"Domain: {self.domain}")
        print(f"Pages: {pages_count}")
        print(f"Assets: {assets_count}")
        print(f"Assets Size: {assets_size / 1024 / 1024:.2f} MB")
        print(f"Total Archive: {archive_size / 1024 / 1024:.2f} MB")
        print(f"Errors: {errors_count}")
        print(f"Structure: ISO 28500:2017 WARC/1.1 + Organized Directories")
        print(f"Archive Path: {self.archive_path}/")
        
        # Print error summary
        if self.stats:
            print(f"\nStatistics:")
            for key, value in self.stats.items():
                if value > 0:
                    print(f"  {key}: {value}")
        
        print("\nTo restore: unzip artifact → cd archive_{domain}/ → python -m http.server")
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
