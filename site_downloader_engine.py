#!/usr/bin/env python3
"""
🔥 SITE DOWNLOADER ENGINE
Integrated downloader using httrack/wget
Saves FULL website (HTML, CSS, JS, images) to database
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

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class SiteDownloaderEngine:
    """🔥 Download full website using httrack/wget and save to DB"""
    
    def __init__(self, conn: sqlite3.Connection, domain: str):
        self.conn = conn
        self.domain = domain
        self._init_tables()
    
    def _init_tables(self):
        """Initialize tables for downloaded site"""
        cursor = self.conn.cursor()
        
        # Downloaded files
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloaded_files (
                id INTEGER PRIMARY KEY,
                domain TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,  -- 'html', 'css', 'js', 'image', etc
                file_size INTEGER,
                content_hash TEXT UNIQUE,
                file_content BLOB,
                url TEXT,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Download metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS download_metadata (
                id INTEGER PRIMARY KEY,
                domain TEXT UNIQUE NOT NULL,
                tool_used TEXT,  -- 'httrack' or 'wget'
                start_url TEXT,
                download_start TIMESTAMP,
                download_end TIMESTAMP,
                total_files INTEGER,
                total_size INTEGER,
                success BOOLEAN,
                error_message TEXT
            )
        ''')
        
        self.conn.commit()
    
    def check_tools(self) -> str:
        """💎 Check which tool is available: httrack or wget"""
        if shutil.which('httrack'):
            logger.info("✅ httrack found - using for download")
            return 'httrack'
        elif shutil.which('wget'):
            logger.info("✅ wget found - using for download")
            return 'wget'
        else:
            logger.error("❌ Neither httrack nor wget found!")
            return None
    
    async def download_with_httrack(self, url: str, output_dir: Path, max_pages: int = 100) -> dict:
        """🔥 Download site using httrack"""
        logger.info(f"🔥 Starting httrack download: {url}")
        logger.info(f"📄 Max pages: {max_pages}")
        
        try:
            # Run httrack
            cmd = [
                'httrack',
                url,
                '-O', str(output_dir),
                '-%e',           # Save structure
                '-k',            # Convert links
                f'-N{max_pages}', # Max files limit
                '--max-rate=0',  # No speed limit
                '-c16',          # 16 threads
                '--continue'     # Continue if interrupted
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"httrack failed: {stderr.decode()}")
                return {'success': False, 'error': stderr.decode()}
            
            logger.info("✅ httrack download complete")
            return {'success': True, 'output_dir': str(output_dir)}
            
        except Exception as e:
            logger.error(f"httrack error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def download_with_wget(self, url: str, output_dir: Path, max_pages: int = 100) -> dict:
        """⚡ Download site using wget with strict page + asset limit"""
        logger.info(f"⚡ Starting wget download: {url}")
        logger.info(f"📄 Config: max_pages={max_pages} HTML files, with --quota hard limit")
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Strategy: 
            # --level 1        = only 1 level deep (start page + direct child links)
            # --accept         = ONLY download .html files + requisites
            # --quota          = hard KB quota (5 pages ≈ 2.5MB with assets)
            # --reject-regex   = block video/large media before download
            # --page-requisites= grab CSS/JS/images from downloaded HTML pages
            
            cmd = [
                'wget',
                '--recursive',
                '--level', '1',                     # Only 1 level deep
                '--accept', '*.html,*.htm',         # Only HTML (+ requisites for those)
                '--page-requisites',                # Grab CSS/JS/images from HTML pages
                '--adjust-extension',
                '--convert-links',
                '--restrict-file-names=windows',
                f'--domains={domain}',
                '--no-parent',
                '--wait', '1',
                '--random-wait',
                '--timeout', '20',
                '--tries', '2',
                '--retry-connrefused',
                f'--quota={max_pages * 500}K',      # Hard quota: pages * 500KB (flexible)
                '--reject-regex', r'\.(webm|mp4|mov|avi|mpeg|mkv|flv|wmv|m4v|ts|mpg|3gp|vob|f4v|wav|mp3|aac|flac|opus)$',
                '--user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                '-P', str(output_dir),
                url
            ]
            
            logger.info(f"🔧 wget params: level=1, accept=*.html, quota={max_pages * 500}K, media blocked")
            logger.info(f"📊 Expected: ~{max_pages} HTML pages + their CSS/JS/images")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode not in [0, 8]:  # 0=OK, 8=server errors (acceptable)
                logger.warning(f"wget returncode: {process.returncode}")
                if process.returncode > 8:
                    logger.error(f"wget failed: {stderr.decode()}")
                    return {'success': False, 'error': stderr.decode()}
            
            logger.info("✅ wget download complete")
            return {'success': True, 'output_dir': str(output_dir)}
            
        except Exception as e:
            logger.error(f"wget error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def download_site(self, url: str, max_pages: int = 100) -> dict:
        """🔥 Download full website and save to DB"""
        logger.info(f"🔥 STARTING WEBSITE DOWNLOAD: {url}")
        logger.info(f"⚙️  Config: max_pages={max_pages}")
        
        # Validate max_pages
        if not isinstance(max_pages, int) or max_pages < 1 or max_pages > 500:
            logger.error(f"❌ Invalid max_pages: {max_pages}. Must be 1-500")
            return {'success': False, 'error': 'max_pages must be 1-500'}
        
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
        cursor.execute('''
            INSERT OR REPLACE INTO download_metadata
            (domain, tool_used, start_url, download_start, download_end, total_files, success)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.domain,
            tool,
            url,
            start_time.isoformat(),
            datetime.now().isoformat(),
            files_processed,
            True
        ))
        self.conn.commit()
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        logger.info(f"✅ DOWNLOAD COMPLETE: {files_processed} files saved")
        
        return {
            'success': True,
            'tool': tool,
            'files_processed': files_processed,
            'url': url,
            'max_pages': max_pages
        }
    
    async def _process_and_save_files(self, base_dir: Path, start_url: str) -> int:
        """💾 Process downloaded files and save to DB"""
        cursor = self.conn.cursor()
        files_count = 0
        
        # Walk through all downloaded files
        for file_path in base_dir.rglob('*'):
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
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    # Calculate hash
                    content_hash = hashlib.sha256(content).hexdigest()
                    
                    # Get file size
                    file_size = len(content)
                    
                    # Get relative path
                    rel_path = str(file_path.relative_to(base_dir))
                    
                    # Save to DB
                    cursor.execute('''
                        INSERT OR IGNORE INTO downloaded_files
                        (domain, file_path, file_type, file_size, content_hash, file_content, url)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        self.domain,
                        rel_path,
                        file_type,
                        file_size,
                        content_hash,
                        content,
                        start_url
                    ))
                    
                    files_count += 1
                    if files_count % 100 == 0:
                        logger.info(f"💾 Processed {files_count} files...")
                    
                except Exception as e:
                    logger.debug(f"Error processing {file_path}: {e}")
        
        self.conn.commit()
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
        """📈 Get download statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM downloaded_files WHERE domain = ?', (self.domain,))
        total_files = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(file_size) FROM downloaded_files WHERE domain = ?', (self.domain,))
        total_size = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT file_type, COUNT(*) FROM downloaded_files 
            WHERE domain = ? GROUP BY file_type
        ''', (self.domain,))
        by_type = dict(cursor.fetchall())
        
        return {
            'total_files': total_files,
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
        print("🚀 DOWNLOAD COMPLETE")
        print("="*70)
        print(f"Total files: {stats['total_files']}")
        print(f"Total size: {stats['total_size_mb']:.2f} MB")
        print(f"By type: {stats['by_type']}")
        print(f"Max pages limit: {result['max_pages']}")
        print("="*70)
    else:
        print(f"\n❌ Download failed: {result['error']}")
    
    conn.close()
