#!/usr/bin/env python3
"""
Asset Extractor - Extract and download assets from HTML
Deduplicated storage with content hashing
"""

import asyncio
import aiohttp
import hashlib
import sqlite3
from urllib.parse import urljoin, urlparse
from pathlib import Path
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class AssetExtractor:
    """Extract and download assets with deduplication"""
    
    # MIME types for different asset types
    MIME_TYPES = {
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.svg': 'image/svg+xml',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.ico': 'image/x-icon',
        '.ttf': 'font/ttf',
        '.woff': 'font/woff',
        '.woff2': 'font/woff2',
    }
    
    def __init__(self, db_conn: sqlite3.Connection):
        self.conn = db_conn
        self.downloaded_hashes = set()
        self._load_existing_hashes()
    
    def _load_existing_hashes(self):
        """Load already downloaded asset hashes"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT content_hash FROM asset_blobs')
            self.downloaded_hashes = {row[0] for row in cursor.fetchall()}
        except:
            pass
    
    def guess_mime_type(self, url: str) -> str:
        """Determine MIME type from URL"""
        url_lower = url.lower()
        for ext, mime in self.MIME_TYPES.items():
            if url_lower.endswith(ext):
                return mime
        return 'application/octet-stream'
    
    def extract_assets(self, html: str, page_url: str) -> list:
        """Extract asset URLs from HTML"""
        try:
            soup = BeautifulSoup(html, 'lxml')
        except:
            soup = BeautifulSoup(html, 'html.parser')
        
        assets = []
        seen = set()
        
        # Images
        for img in soup.find_all('img', src=True):
            src = img['src'].strip()
            if src and not src.startswith('data:'):
                url = urljoin(page_url, src)
                if url not in seen:
                    seen.add(url)
                    assets.append({
                        'url': url,
                        'type': 'image',
                        'mime': self.guess_mime_type(url),
                    })
        
        # Stylesheets
        for link in soup.find_all('link'):
            if link.get('rel') and 'stylesheet' in link.get('rel', []):
                href = link.get('href', '').strip()
                if href and not href.startswith('data:'):
                    url = urljoin(page_url, href)
                    if url not in seen:
                        seen.add(url)
                        assets.append({
                            'url': url,
                            'type': 'css',
                            'mime': 'text/css',
                        })
        
        # Scripts
        for script in soup.find_all('script', src=True):
            src = script['src'].strip()
            if src and not src.startswith('data:'):
                url = urljoin(page_url, src)
                if url not in seen:
                    seen.add(url)
                    assets.append({
                        'url': url,
                        'type': 'js',
                        'mime': 'application/javascript',
                    })
        
        # Favicon
        for link in soup.find_all('link'):
            if link.get('rel'):
                rels = link.get('rel', [])
                if any(r in ['icon', 'shortcut icon'] for r in rels):
                    href = link.get('href', '').strip()
                    if href and not href.startswith('data:'):
                        url = urljoin(page_url, href)
                        if url not in seen:
                            seen.add(url)
                            assets.append({
                                'url': url,
                                'type': 'image',
                                'mime': self.guess_mime_type(url),
                            })
        
        # Meta images (Open Graph, Twitter Card)
        for meta in soup.find_all('meta'):
            prop_or_name = meta.get('property') or meta.get('name')
            if prop_or_name and any(x in prop_or_name.lower() for x in ['og:image', 'twitter:image']):
                content = meta.get('content', '').strip()
                if content and not content.startswith('data:'):
                    url = urljoin(page_url, content)
                    if url not in seen:
                        seen.add(url)
                        assets.append({
                            'url': url,
                            'type': 'image',
                            'mime': self.guess_mime_type(url),
                        })
        
        return assets
    
    async def download_and_save_asset(self, asset: dict, domain: str, session) -> dict:
        """Download asset and save to database (sync wrapper)"""
        result = {'downloaded': 0, 'failed': 0, 'skipped': 0}
        
        url = asset.get('url', '').strip()
        asset_type = asset.get('type', 'unknown')
        mime_type = asset.get('mime', 'application/octet-stream')
        
        if not url:
            result['failed'] += 1
            return result
        
        try:
            # Download
            async with session.get(url, ssl=True, timeout=aiohttp.ClientTimeout(total=30), allow_redirects=True) as response:
                if response.status != 200:
                    result['failed'] += 1
                    return result
                
                # Read content
                content = await response.read()
                
                if not content or len(content) == 0:
                    result['failed'] += 1
                    return result
                
                # Calculate hash
                content_hash = hashlib.sha256(content).hexdigest()
                
                # Check if already downloaded
                if content_hash in self.downloaded_hashes:
                    result['skipped'] += 1
                    return result
                
                # Parse URL for path
                parsed = urlparse(url)
                path = parsed.path or '/'
                
                # Save to database
                try:
                    cursor = self.conn.cursor()
                    
                    # Save blob (deduplicated)
                    cursor.execute('''
                        INSERT OR IGNORE INTO asset_blobs (content_hash, content)
                        VALUES (?, ?)
                    ''', (content_hash, content))
                    
                    # Save asset reference
                    cursor.execute('''
                        INSERT OR IGNORE INTO assets 
                        (url, domain, path, asset_type, content_hash, file_size, mime_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (url, domain, path, asset_type, content_hash, len(content), mime_type))
                    
                    self.conn.commit()
                    self.downloaded_hashes.add(content_hash)
                    result['downloaded'] += 1
                    logger.debug(f"Saved asset: {url} ({len(content)} bytes)")
                    
                except sqlite3.IntegrityError as e:
                    # Already exists (unique constraint)
                    result['skipped'] += 1
                except Exception as e:
                    logger.error(f"DB error saving {url}: {e}")
                    result['failed'] += 1
                
        except asyncio.TimeoutError:
            logger.debug(f"Timeout: {url}")
            result['failed'] += 1
        except Exception as e:
            logger.debug(f"Error downloading {url}: {type(e).__name__}: {e}")
            result['failed'] += 1
        
        return result
