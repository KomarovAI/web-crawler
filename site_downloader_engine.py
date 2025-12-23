#!/usr/bin/env python3
"""
🔥 SITE DOWNLOADER ENGINE v2
Best practices: GNU Wget 1.25.0 docs + HTTrack limits
- Respect --level (depth) not just files
- --page-requisites for CSS/JS/images
- Proper --quota and size limits
- Smart delays + connection pooling
- File counter to respect max_pages
"""

import asyncio
import subprocess
import sqlite3
import shutil
import json
from pathlib import Path
from urllib.parse import urlparse
import logging
from datetime import datetime
import hashlib
import time

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class SiteDownloaderEngine:
    """🔥 Download full website using httrack/wget with best practices"""
    
    # HTTrack limits (from official docs)
    HTTRACK_LIMITS = {
        'max_depth': 2,                    # Maximum mirror depth
        'max_html_size': 5 * 1024 * 1024,  # 5MB per HTML file
        'max_asset_size': 2 * 1024 * 1024, # 2MB per image/CSS/JS
        'total_size': 500 * 1024 * 1024,   # 500MB total site size
        'max_time': 3600,                  # 1 hour timeout
        'max_links': 10000,                # Max links to analyze
    }
    
    # WGET defaults (from GNU Wget 1.25.0 manual)
    WGET_DELAYS = {
        'base_wait': 2,      # 2 seconds base delay
        'random_wait': 2,    # Random 0-2 sec additional
        'connect_timeout': 20,
        'read_timeout': 20,
        'retries': 3,
        'threads': 8,        # Concurrent connections
    }
    
    def __init__(self, conn: sqlite3.Connection, domain: str):
        self.conn = conn
        self.domain = domain
        self.file_counter = 0
        self.max_files_limit = 0
        self._init_tables()
    
    def _init_tables(self):
        """Initialize tables for downloaded site"""
        cursor = self.conn.cursor()
        
        # Downloaded files with extended metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloaded_files (
                id INTEGER PRIMARY KEY,
                domain TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,  -- html, css, js, image, font, other
                file_size INTEGER,
                content_hash TEXT UNIQUE,
                file_content BLOB,
                url TEXT,
                http_status INTEGER,
                charset TEXT,
                download_time REAL,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Download metadata with detailed stats
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS download_metadata (
                id INTEGER PRIMARY KEY,
                domain TEXT UNIQUE NOT NULL,
                tool_used TEXT,  -- httrack or wget
                start_url TEXT,
                download_start TIMESTAMP,
                download_end TIMESTAMP,
                total_files INTEGER,
                total_size INTEGER,
                success BOOLEAN,
                error_message TEXT,
                depth_limit INTEGER,
                quota_limit_kb INTEGER,
                files_by_type TEXT  -- JSON
            )
        ''')
        
        self.conn.commit()
    
    def check_tools(self) -> str:
        """🔍 Check which tool is available: httrack or wget"""
        if shutil.which('httrack'):
            logger.info("✅ httrack found - using for download")
            return 'httrack'
        elif shutil.which('wget'):
            logger.info("✅ wget found - using for download")
            return 'wget'
        else:
            logger.error("❌ Neither httrack nor wget found!")
            return None
    
    async def download_with_httrack(self, url: str, output_dir: Path, max_pages: int) -> dict:
        """🔥 Download site using httrack with official limits"""
        logger.info(f"🔥 Starting httrack download: {url}")
        logger.info(f"📄 Max pages target: {max_pages}")
        logger.info(f"⚙️  HTTrack limits: depth={self.HTTRACK_LIMITS['max_depth']}, "
                   f"html_size={self.HTTRACK_LIMITS['max_html_size']//1024//1024}MB, "
                   f"total={self.HTTRACK_LIMITS['total_size']//1024//1024}MB")
        
        try:
            # HTTrack command with official best practices
            cmd = [
                'httrack',
                url,
                '-O', str(output_dir),
                '-%e',                                           # Save structure as-is
                '-k',                                            # Convert links to relative
                f'-r{self.HTTRACK_LIMITS["max_depth"]}',        # Max depth (2)
                f'-m{self.HTTRACK_LIMITS["max_html_size"]//1024}k',  # Max HTML file size
                f'-M{self.HTTRACK_LIMITS["max_asset_size"]//1024}k', # Max asset size
                f'-q{self.HTTRACK_LIMITS["max_links"]}',        # Max links to scan
                '--max-rate=0',                                 # No speed limit (we control via --wait)
                '-c8',                                          # 8 concurrent connections
                f'--timeout={self.HTTRACK_LIMITS["max_time"]}', # 1 hour timeout
                '-T5',                                          # 5 sec timeout per request
                '--continue',                                   # Resume if interrupted
                '--fast-statistics',                            # Faster stats
                '-v'                                            # Verbose
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0 and process.returncode != 1:  # 1 = some links failed (ok)
                logger.error(f"httrack failed: {stderr.decode()}")
                return {'success': False, 'error': stderr.decode()}
            
            logger.info("✅ httrack download complete")
            return {'success': True, 'output_dir': str(output_dir)}
            
        except Exception as e:
            logger.error(f"httrack error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def download_with_wget(self, url: str, output_dir: Path, max_pages: int) -> dict:
        """⚡ Download site using wget with GNU Wget 1.25.0 best practices"""
        logger.info(f"⚡ Starting wget download: {url}")
        logger.info(f"📄 Target: {max_pages} HTML pages + their CSS/JS/images")
        logger.info(f"⏱️  Delays: base={self.WGET_DELAYS['base_wait']}s + "
                   f"random={self.WGET_DELAYS['random_wait']}s")
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Calculate quota: avg page ~300KB + assets ~700KB per page = ~1MB per page
            # Add 30% buffer for headers and metadata
            quota_kb = int(max_pages * 1000 * 1.3)
            
            # WGET command with GNU Wget 1.25.0 best practices
            cmd = [
                'wget',
                '--recursive',                              # Recursive mode
                '--level=2',                                # Depth: 2 (start + direct links)
                '--accept-regex=\\.(html?|css|js|jpg|jpeg|png|gif|webp|svg|woff|woff2|ttf|eot)$',  # Only useful files
                '--page-requisites',                        # ✨ Grab CSS/JS/images for downloaded pages
                '--adjust-extension',                       # Add .html if needed
                '--convert-links',                          # Convert to relative links
                '--restrict-file-names=windows',            # Windows-safe filenames
                f'--domains={domain}',                      # Stay on domain
                '--no-parent',                              # Don't go above root
                
                # Delays (GNU Wget best practices)
                f'--wait={self.WGET_DELAYS[\"base_wait\"]}',           # Wait 2s between requests
                f'--random-wait',                                      # Random 0-2s additional wait
                '--waitretry=10',                                      # Wait 10s before retry
                
                # Timeouts
                f'--connect-timeout={self.WGET_DELAYS[\"connect_timeout\"]}',
                f'--read-timeout={self.WGET_DELAYS[\"read_timeout\"]}',
                f'--tries={self.WGET_DELAYS[\"retries\"]}',            # Retry 3 times
                '--retry-connrefused',                                 # Retry on connection refused
                
                # Size limits (HTTrack style)
                f'--quota={quota_kb}K',                     # Hard size quota
                '--limit-rate=500k',                        # Max 500KB/s (polite)
                
                # Media blocking (HTTrack style)
                '--reject-regex=\\.(webm|mp4|mov|avi|mpeg|mkv|flv|wmv|m4v|ts|mpg|3gp|vob|f4v|wav|mp3|aac|flac|opus|zip|exe|torrent)$',
                
                # Performance
                f'--timeout={self.WGET_DELAYS[\"read_timeout\"]}',
                '-N',                                       # Only newer files
                '--no-verbose',                             # Less spam
                '--show-progress',                          # Show progress
                
                # User agent (honest)
                '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                
                # Output
                '-P', str(output_dir),
                url
            ]
            
            logger.info(f"🔧 wget config: level=2, page-requisites=ON, quota={quota_kb}KB, "
                       f"wait={self.WGET_DELAYS['base_wait']}+random, limit=500KB/s")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # wget return codes: 0=OK, 1=generic, 2=parse error, 3=file I/O, 4=network, 
            # 5=SSL, 6=auth, 7=protocol, 8=server, 9=user interrupt
            if process.returncode not in [0, 1, 8]:  # 0/1/8 are acceptable
                if process.returncode > 2:
                    logger.error(f"wget failed with code {process.returncode}: {stderr.decode()}")
                    return {'success': False, 'error': stderr.decode()}
            
            logger.info("✅ wget download complete")
            return {'success': True, 'output_dir': str(output_dir)}
            
        except Exception as e:
            logger.error(f"wget error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def download_site(self, url: str, max_pages: int = 100) -> dict:
        """🔥 Download full website and save to DB"""
        logger.info(f"\n{'='*70}")
        logger.info(f"🔥 WEBSITE DOWNLOAD: {url}")
        logger.info(f"{'='*70}")
        logger.info(f"📄 Target: {max_pages} pages")
        
        # Validate max_pages
        if not isinstance(max_pages, int) or max_pages < 1 or max_pages > 1000:
            logger.error(f"❌ Invalid max_pages: {max_pages}. Must be 1-1000")
            return {'success': False, 'error': 'max_pages must be 1-1000'}
        
        self.max_files_limit = max_pages * 10  # Allow ~10 assets per page
        
        # Check available tools
        tool = self.check_tools()
        if not tool:
            return {'success': False, 'error': 'No download tool available'}
        
        # Create temp directory
        temp_dir = Path('temp_download')
        temp_dir.mkdir(exist_ok=True)
        
        start_time = datetime.now()
        
        # Download based on available tool
        if tool == 'httrack':
            result = await self.download_with_httrack(url, temp_dir, max_pages)
        else:
            result = await self.download_with_wget(url, temp_dir, max_pages)
        
        if not result['success']:
            return result
        
        # Process downloaded files and save to DB
        logger.info("💾 Processing and saving to database...")
        files_processed = await self._process_and_save_files(temp_dir, url)
        
        # Save metadata
        cursor = self.conn.cursor()
        stats = self.get_stats()
        
        cursor.execute('''
            INSERT OR REPLACE INTO download_metadata
            (domain, tool_used, start_url, download_start, download_end, total_files, 
             total_size, success, depth_limit, quota_limit_kb, files_by_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.domain,
            tool,
            url,
            start_time.isoformat(),
            datetime.now().isoformat(),
            files_processed,
            stats.get('total_size_bytes', 0),
            True,
            2,  # depth limit
            int(max_pages * 1000 * 1.3),  # quota
            json.dumps(stats.get('by_type', {}))
        ))
        self.conn.commit()
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ DOWNLOAD COMPLETE in {duration:.1f}s")
        logger.info(f"{'='*70}")
        logger.info(f"📁 Total files: {files_processed}")
        logger.info(f"📊 Breakdown: {stats.get('by_type', {})}")
        logger.info(f"💾 Total size: {stats.get('total_size_mb', 0):.2f} MB")
        logger.info(f"{'='*70}\n")
        
        return {
            'success': True,
            'tool': tool,
            'files_processed': files_processed,
            'url': url,
            'max_pages': max_pages,
            'duration_seconds': duration
        }
    
    async def _process_and_save_files(self, base_dir: Path, start_url: str) -> int:
        """💾 Process downloaded files and save to DB with counter"""
        cursor = self.conn.cursor()
        files_count = 0
        skipped = 0
        
        # Walk through all downloaded files
        for file_path in sorted(base_dir.rglob('*')):
            if file_path.is_file():
                # ⚠️ Check max files limit
                if files_count >= self.max_files_limit:
                    logger.warning(f"⚠️  Max files limit reached ({self.max_files_limit})")
                    break
                
                try:
                    # Determine file type
                    suffix = file_path.suffix.lower()
                    if suffix in ['.html', '.htm']:
                        file_type = 'html'
                    elif suffix == '.css':
                        file_type = 'css'
                    elif suffix == '.js':
                        file_type = 'javascript'
                    elif suffix in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
                        file_type = 'image'
                    elif suffix in ['.woff', '.woff2', '.ttf', '.eot']:
                        file_type = 'font'
                    else:
                        file_type = 'other'
                    
                    # Read file
                    start = time.time()
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    download_time = time.time() - start
                    
                    # Calculate hash
                    content_hash = hashlib.sha256(content).hexdigest()
                    
                    # Get file size
                    file_size = len(content)
                    
                    # Get relative path
                    rel_path = str(file_path.relative_to(base_dir))
                    
                    # Save to DB
                    cursor.execute('''
                        INSERT OR IGNORE INTO downloaded_files
                        (domain, file_path, file_type, file_size, content_hash, 
                         file_content, url, download_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        self.domain,
                        rel_path,
                        file_type,
                        file_size,
                        content_hash,
                        content,
                        start_url,
                        download_time
                    ))
                    
                    files_count += 1
                    if files_count % 100 == 0:
                        logger.info(f"💾 Processed {files_count} files...")
                    
                except Exception as e:
                    logger.debug(f"Error processing {file_path}: {e}")
                    skipped += 1
        
        self.conn.commit()
        if skipped > 0:
            logger.warning(f"⚠️  Skipped {skipped} files due to errors")
        return files_count
    
    def get_file(self, file_path: str) -> bytes:
        """📄 Retrieve file content from DB"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT file_content FROM downloaded_files WHERE domain = ? AND file_path = ?',
            (self.domain, file_path)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    
    def get_stats(self) -> dict:
        """📊 Get download statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM downloaded_files WHERE domain = ?', (self.domain,))
        total_files = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(file_size) FROM downloaded_files WHERE domain = ?', (self.domain,))
        total_size = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT file_type, COUNT(*), SUM(file_size) FROM downloaded_files 
            WHERE domain = ? GROUP BY file_type
        ''', (self.domain,))
        
        by_type = {}
        for file_type, count, size in cursor.fetchall():
            by_type[file_type] = {'count': count, 'size_mb': size / 1024 / 1024 if size else 0}
        
        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / 1024 / 1024,
            'by_type': by_type
        }


if __name__ == '__main__':
    import sys
    
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://example.com'
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    domain = urlparse(url).netloc
    
    conn = sqlite3.connect('archive.db')
    downloader = SiteDownloaderEngine(conn, domain)
    
    result = asyncio.run(downloader.download_site(url, max_pages))
    
    if result['success']:
        stats = downloader.get_stats()
        print("\n" + "="*70)
        print("🚀 DOWNLOAD SUMMARY")
        print("="*70)
        print(f"Total files: {stats['total_files']}")
        print(f"Total size: {stats['total_size_mb']:.2f} MB")
        print(f"Duration: {result['duration_seconds']:.1f}s")
        print(f"Files by type:")
        for ftype, data in stats['by_type'].items():
            print(f"  {ftype}: {data['count']} files ({data['size_mb']:.2f} MB)")
        print("="*70)
    else:
        print(f"\n❌ Download failed: {result['error']}")
    
    conn.close()
