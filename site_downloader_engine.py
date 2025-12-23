#!/usr/bin/env python3
"""
🔥 SITE DOWNLOADER ENGINE v4
PROPER LEVEL-BASED CRAWLING (забыли о max_pages!)
- depth_level: 1-4 (controls actual crawl depth, not file count)
- wget --level=N works PREDICTABLY
- --quota as safety net only

Level mapping:
  1 = start page only
  2 = start + direct child links (most useful)
  3 = start + children + grandchildren
  4 = deep crawl (be careful!)
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
    """🔥 Download website using wget with LEVEL-BASED control (NOT max_pages)"""
    
    # Strict file size limits
    FILE_SIZE_LIMITS = {
        'html': 300 * 1024,         # 300KB per HTML
        'css': 50 * 1024,           # 50KB per CSS
        'javascript': 150 * 1024,   # 150KB per JS
        'image': 150 * 1024,        # 150KB per image
        'font': 100 * 1024,         # 100KB per font
        'other': 50 * 1024,         # 50KB other
    }
    
    # Level-based quotas (safety nets)
    LEVEL_QUOTAS = {
        1: 2000,      # Level 1: start page only → 2MB quota
        2: 10000,     # Level 2: start + direct children → 10MB quota
        3: 50000,     # Level 3: deeper crawl → 50MB quota
        4: 200000,    # Level 4: very deep → 200MB quota (be careful!)
    }
    
    # WGET parameters
    WGET_PARAMS = {
        'wait': 1.5,             # 1.5 sec between requests
        'random_wait': 1.5,      # +0-1.5 sec random
        'connect_timeout': 20,
        'read_timeout': 20,
        'retries': 2,
        'limit_rate': 256,       # 256KB/s max
    }
    
    def __init__(self, conn: sqlite3.Connection, domain: str):
        self.conn = conn
        self.domain = domain
        self.files_skipped = 0
        self.files_saved = 0
        self._init_tables()
    
    def _init_tables(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloaded_files (
                id INTEGER PRIMARY KEY,
                domain TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER,
                content_hash TEXT UNIQUE,
                file_content BLOB,
                url TEXT,
                download_time REAL,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS download_metadata (
                id INTEGER PRIMARY KEY,
                domain TEXT UNIQUE NOT NULL,
                tool_used TEXT,
                start_url TEXT,
                depth_level INTEGER,
                download_start TIMESTAMP,
                download_end TIMESTAMP,
                total_files INTEGER,
                files_skipped INTEGER,
                total_size INTEGER,
                success BOOLEAN,
                error_message TEXT,
                files_by_type TEXT
            )
        ''')
        
        self.conn.commit()
    
    def check_tools(self) -> str:
        """🔍 Check available tool"""
        if shutil.which('httrack'):
            logger.info("✅ httrack found")
            return 'httrack'
        elif shutil.which('wget'):
            logger.info("✅ wget found")
            return 'wget'
        else:
            logger.error("❌ No download tool available!")
            return None
    
    async def download_with_wget(self, url: str, output_dir: Path, depth_level: int) -> dict:
        """⚡ Download with wget using LEVEL control"""
        logger.info(f"⚡ Starting wget: {url}")
        logger.info(f"📊 Depth level: {depth_level}")
        logger.info(f"📋 Level description: {self._get_level_description(depth_level)}")
        
        # Validate depth level
        if depth_level < 1 or depth_level > 4:
            logger.error(f"❌ Invalid depth_level: {depth_level} (must be 1-4)")
            return {'success': False, 'error': 'depth_level must be 1-4'}
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Get quota for this level
            quota_kb = self.LEVEL_QUOTAS.get(depth_level, 10000)
            
            cmd = [
                'wget',
                '--recursive',
                f'--level={depth_level}',          # 🔑 KEY: Level control
                
                # File type filtering (strict)
                '--accept-regex=\\.(html?|css|js|jpg|jpeg|png|gif|webp|svg|woff|woff2|ttf|eot)$',
                '--reject-regex=\\.(webm|mp4|mov|avi|mpeg|mkv|flv|wmv|m4v|ts|mpg|3gp|vob|f4v|wav|mp3|aac|flac|opus|zip|exe|torrent|pdf|doc|docx|xls|xlsx)$',
                
                # Get assets for downloaded pages only
                '--page-requisites',
                '--no-remove-listing',
                
                # Link conversion
                '--adjust-extension',
                '--convert-links',
                '--restrict-file-names=windows',
                f'--domains={domain}',
                '--no-parent',
                
                # Politeness delays
                f'--wait={self.WGET_PARAMS["wait"]}',
                '--random-wait',
                '--waitretry=5',
                
                # Timeouts
                f'--connect-timeout={self.WGET_PARAMS["connect_timeout"]}',
                f'--read-timeout={self.WGET_PARAMS["read_timeout"]}',
                f'--tries={self.WGET_PARAMS["retries"]}',
                '--retry-connrefused',
                
                # Size safety net
                f'--quota={quota_kb}K',
                f'--limit-rate={self.WGET_PARAMS["limit_rate"]}k',
                
                # Optimization
                '-N',
                '--no-verbose',
                '--show-progress',
                
                # User agent
                '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                
                '-P', str(output_dir),
                url
            ]
            
            logger.info(f"🔧 wget config: level={depth_level}, quota={quota_kb}KB, "
                       f"wait={self.WGET_PARAMS['wait']}s, limit={self.WGET_PARAMS['limit_rate']}KB/s")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode not in [0, 1, 8]:
                if process.returncode > 2:
                    error_msg = stderr.decode()[-500:]
                    logger.error(f"wget failed (code {process.returncode}): {error_msg}")
                    return {'success': False, 'error': error_msg}
            
            logger.info("✅ wget complete")
            return {'success': True, 'output_dir': str(output_dir)}
            
        except Exception as e:
            logger.error(f"wget error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def download_site(self, url: str, depth_level: int = 2) -> dict:
        """🔥 Download website using depth_level (NOT max_pages)"""
        logger.info(f"\n{'='*70}")
        logger.info(f"🔥 WEBSITE DOWNLOAD: {url}")
        logger.info(f"{'='*70}")
        logger.info(f"📊 Depth Level: {depth_level} ({self._get_level_description(depth_level)})")
        
        # Validate
        if not isinstance(depth_level, int) or depth_level < 1 or depth_level > 4:
            logger.error(f"❌ Invalid depth_level: {depth_level}. Must be 1-4")
            return {'success': False, 'error': 'depth_level must be 1-4'}
        
        # Check tools
        tool = self.check_tools()
        if not tool:
            return {'success': False, 'error': 'No download tool available'}
        
        # Create temp dir
        temp_dir = Path('temp_download')
        temp_dir.mkdir(exist_ok=True)
        
        start_time = datetime.now()
        
        # Download
        result = await self.download_with_wget(url, temp_dir, depth_level)
        
        if not result['success']:
            return result
        
        # Process files
        logger.info("📦 Processing files...")
        files_processed = await self._process_and_save_files(temp_dir, url)
        
        # Save metadata
        cursor = self.conn.cursor()
        stats = self.get_stats()
        
        cursor.execute('''
            INSERT OR REPLACE INTO download_metadata
            (domain, tool_used, start_url, depth_level, download_start, download_end,
             total_files, files_skipped, total_size, success, files_by_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.domain,
            tool,
            url,
            depth_level,
            start_time.isoformat(),
            datetime.now().isoformat(),
            files_processed,
            self.files_skipped,
            stats.get('total_size_bytes', 0),
            True,
            json.dumps(stats.get('by_type', {}))
        ))
        self.conn.commit()
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ COMPLETE in {duration:.1f}s")
        logger.info(f"{'='*70}")
        logger.info(f"📄 Files saved: {files_processed}")
        logger.info(f"⏭️  Files skipped: {self.files_skipped}")
        logger.info(f"💾 Total size: {stats.get('total_size_mb', 0):.2f}MB")
        logger.info(f"📊 Breakdown: {stats.get('by_type', {})}")
        logger.info(f"{'='*70}\n")
        
        return {
            'success': True,
            'tool': tool,
            'files_processed': files_processed,
            'files_skipped': self.files_skipped,
            'url': url,
            'depth_level': depth_level,
            'duration_seconds': duration,
            'total_size_mb': stats.get('total_size_mb', 0)
        }
    
    async def _process_and_save_files(self, base_dir: Path, start_url: str) -> int:
        """📦 Process files with size filtering"""
        cursor = self.conn.cursor()
        files_count = 0
        
        for file_path in sorted(base_dir.rglob('*')):
            if file_path.is_file():
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
                    
                    file_size = len(content)
                    
                    # Check size limit
                    max_size = self.FILE_SIZE_LIMITS.get(file_type, self.FILE_SIZE_LIMITS['other'])
                    if file_size > max_size:
                        logger.debug(f"⏭️  {file_path.name} oversized ({file_size//1024}KB > {max_size//1024}KB)")
                        self.files_skipped += 1
                        continue
                    
                    # Calculate hash
                    content_hash = hashlib.sha256(content).hexdigest()
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
                    if files_count % 50 == 0:
                        logger.info(f"📦 Processed {files_count} files...")
                    
                except Exception as e:
                    logger.debug(f"Error processing {file_path}: {e}")
                    self.files_skipped += 1
        
        self.conn.commit()
        return files_count
    
    def get_file(self, file_path: str) -> bytes:
        """📄 Get file from DB"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT file_content FROM downloaded_files WHERE domain = ? AND file_path = ?',
            (self.domain, file_path)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    
    def get_stats(self) -> dict:
        """📊 Get statistics"""
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
            by_type[file_type] = {
                'count': count,
                'size_mb': size / 1024 / 1024 if size else 0
            }
        
        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / 1024 / 1024,
            'by_type': by_type
        }
    
    @staticmethod
    def _get_level_description(level: int) -> str:
        """Get human-readable level description"""
        descriptions = {
            1: "Start page only (fastest)",
            2: "Start + direct child pages (recommended)",
            3: "Start + children + grandchildren (deeper)",
            4: "Very deep crawl (slow, be careful!)",
        }
        return descriptions.get(level, "Unknown")


if __name__ == '__main__':
    import sys
    
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://example.com'
    depth_level = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    domain = urlparse(url).netloc
    
    conn = sqlite3.connect('archive.db')
    downloader = SiteDownloaderEngine(conn, domain)
    
    result = asyncio.run(downloader.download_site(url, depth_level))
    
    if result['success']:
        print(f"\n{'='*70}")
        print("✅ SUCCESS")
        print(f"{'='*70}")
        print(f"Files saved: {result['files_processed']}")
        print(f"Files skipped: {result['files_skipped']}")
        print(f"Total size: {result['total_size_mb']:.2f}MB")
        print(f"Duration: {result['duration_seconds']:.1f}s")
        print(f"Depth level: {result['depth_level']}")
        print(f"{'='*70}")
    else:
        print(f"\n❌ Failed: {result['error']}")
    
    conn.close()
