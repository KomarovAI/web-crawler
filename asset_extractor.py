import hashlib
import asyncio
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import aiohttp
import logging

logger = logging.getLogger(__name__)

class AssetExtractor:
    """Извлечение и скачивание ассетов из HTML"""
    
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
    
    def __init__(self, conn):
        self.conn = conn
    
    def guess_mime_type(self, url: str) -> str:
        """Определить MIME тип по URL"""
        url_lower = url.lower()
        for ext, mime in self.MIME_TYPES.items():
            if url_lower.endswith(ext):
                return mime
        return 'application/octet-stream'
    
    def extract_assets(self, html: str, base_url: str) -> list:
        """Найти все ассеты в HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return []
        
        assets = []
        
        # 1. Images
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and src.strip() and not src.startswith('data:'):
                url = urljoin(base_url, src)
                assets.append({
                    'url': url,
                    'type': 'image',
                    'mime': self.guess_mime_type(src),
                    'element': 'img'
                })
        
        # 2. CSS
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href and href.strip():
                url = urljoin(base_url, href)
                assets.append({
                    'url': url,
                    'type': 'css',
                    'mime': 'text/css',
                    'element': 'link'
                })
        
        # 3. Scripts
        for script in soup.find_all('script'):
            src = script.get('src')
            if src and src.strip():
                url = urljoin(base_url, src)
                assets.append({
                    'url': url,
                    'type': 'js',
                    'mime': 'application/javascript',
                    'element': 'script'
                })
        
        # 4. Favicon
        for link in soup.find_all('link', rel=['icon', 'shortcut icon']):
            href = link.get('href')
            if href and href.strip():
                url = urljoin(base_url, href)
                assets.append({
                    'url': url,
                    'type': 'favicon',
                    'mime': self.guess_mime_type(href),
                    'element': 'link'
                })
        
        # 5. Meta images (OG, Twitter)
        for meta in soup.find_all('meta'):
            prop = meta.get('property') or meta.get('name')
            if prop and 'image' in prop.lower():
                content = meta.get('content')
                if content and content.strip():
                    url = urljoin(base_url, content)
                    assets.append({
                        'url': url,
                        'type': 'meta-image',
                        'mime': self.guess_mime_type(content),
                        'element': 'meta'
                    })
        
        # Remove duplicates
        seen = set()
        unique_assets = []
        for asset in assets:
            url = asset['url']
            if url and url not in seen:
                seen.add(url)
                unique_assets.append(asset)
        
        return unique_assets
    
    async def download_asset(self, session, url: str, timeout: int = 10) -> bytes:
        """Скачать один ассет"""
        try:
            async with session.get(url, timeout=timeout, ssl=False) as resp:
                if resp.status == 200:
                    return await resp.read()
                else:
                    logger.warning(f"HTTP {resp.status} for {url}")
        except asyncio.TimeoutError:
            logger.warning(f"Timeout downloading {url}")
        except Exception as e:
            logger.debug(f"Failed to download {url}: {e}")
        return None
    
    async def asset_exists(self, url: str) -> bool:
        """Проверить существует ли ассет в БД"""
        try:
            cursor = self.conn.execute(
                'SELECT id FROM assets WHERE url = ? LIMIT 1',
                (url,)
            )
            return cursor.fetchone() is not None
        except:
            return False
    
    async def save_asset(self, url: str, content: bytes, domain: str, 
                        asset_type: str, mime: str) -> bool:
        """Сохранить ассет в БД"""
        if not content:
            return False
        
        try:
            content_hash = hashlib.sha256(content).hexdigest()
            
            # INSERT OR IGNORE INTO asset_blobs
            self.conn.execute('''
                INSERT OR IGNORE INTO asset_blobs 
                (content_hash, content)
                VALUES (?, ?)
            ''', (content_hash, content))
            
            # INSERT INTO assets
            self.conn.execute('''
                INSERT INTO assets 
                (url, content_hash, mime_type, asset_type, domain, extracted_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (url, content_hash, mime, asset_type, domain))
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving asset {url}: {e}")
            return False
    
    async def download_and_save_assets(self, assets: list, domain: str, 
                                      session) -> dict:
        """Скачать и сохранить все ассеты"""
        downloaded = 0
        failed = 0
        skipped = 0
        
        for asset in assets:
            url = asset['url']
            
            # Skip если уже есть
            if await self.asset_exists(url):
                skipped += 1
                continue
            
            # Скачать
            content = await self.download_asset(session, url)
            if content:
                # Сохранить
                if await self.save_asset(url, content, domain, asset['type'], asset['mime']):
                    downloaded += 1
                    logger.info(f"✅ {asset['type']}: {url}")
                else:
                    failed += 1
            else:
                failed += 1
        
        return {
            'downloaded': downloaded,
            'failed': failed,
            'skipped': skipped,
            'total': len(assets)
        }
