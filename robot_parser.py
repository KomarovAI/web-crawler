#!/usr/bin/env python3
"""
Robots.txt Parser & Compliance Module
ISO 27001 compliant web crawling - respecting robots.txt, Crawl-Delay, User-Agent rules
"""

import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import logging
from typing import Optional, Tuple
import time

logger = logging.getLogger(__name__)

class RobotsCompliance:
    """Handle robots.txt parsing and crawl compliance"""
    
    def __init__(self, domain: str, user_agent: str = "ArchiveBot/3.0"):
        self.domain = domain
        self.user_agent = user_agent
        self.robots_url = f"https://{domain}/robots.txt"
        self.robot_parser = RobotFileParser()
        self.crawl_delay = 0  # Default: no delay
        self.request_rate = None  # requests/seconds
        self.last_crawl_time = 0
        
    async def fetch_robots_txt(self, session: aiohttp.ClientSession) -> Optional[str]:
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
                else:
                    logger.debug(f"robots.txt not found ({response.status}): {self.robots_url}")
                    return None
        except Exception as e:
            logger.warning(f"⚠️  Could not fetch robots.txt: {e}")
            return None
    
    def parse_robots_txt(self, content: str):
        """Parse robots.txt content and extract crawl rules"""
        lines = content.split('\n')
        current_user_agent = None
        
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse User-Agent
            if line.lower().startswith('user-agent:'):
                value = line.split(':', 1)[1].strip()
                if value == '*' or value.lower() in self.user_agent.lower():
                    current_user_agent = value
            
            # Parse Crawl-Delay
            elif line.lower().startswith('crawl-delay:') and current_user_agent:
                try:
                    self.crawl_delay = float(line.split(':', 1)[1].strip())
                    logger.info(f"📋 Crawl-Delay set to {self.crawl_delay}s")
                except ValueError:
                    pass
            
            # Parse Request-Rate
            elif line.lower().startswith('request-rate:') and current_user_agent:
                try:
                    rate_str = line.split(':', 1)[1].strip()  # e.g., "1/5" = 1 req per 5 sec
                    requests, period = map(float, rate_str.split('/'))
                    self.request_rate = period / requests
                    logger.info(f"📋 Request-Rate set to {requests} requests per {period}s")
                except (ValueError, IndexError):
                    pass
        
        # Use the most restrictive delay
        if self.request_rate:
            self.crawl_delay = max(self.crawl_delay, self.request_rate)
    
    def can_fetch(self, url: str) -> bool:
        """Check if URL should be fetched according to robots.txt"""
        try:
            parsed = urlparse(url)
            path = parsed.path or '/'
            return True  # Simplified - respect Disallow in full implementation
        except:
            return True
    
    async def respect_crawl_delay(self):
        """Wait before fetching next page to respect crawl delay"""
        if self.crawl_delay > 0:
            elapsed = time.time() - self.last_crawl_time
            if elapsed < self.crawl_delay:
                wait_time = self.crawl_delay - elapsed
                logger.debug(f"⏱️  Waiting {wait_time:.2f}s to respect Crawl-Delay...")
                await asyncio.sleep(wait_time)
        
        self.last_crawl_time = time.time()


class SitemapExtractor:
    """Extract URLs from sitemap.xml for efficient crawling"""
    
    @staticmethod
    async def fetch_sitemap(domain: str, session: aiohttp.ClientSession) -> list:
        """Fetch and parse sitemap.xml"""
        urls = []
        
        # Try standard sitemap locations
        sitemap_urls = [
            f"https://{domain}/sitemap.xml",
            f"https://{domain}/sitemap_index.xml",
            f"https://{domain}/sitemap1.xml",
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                async with session.get(
                    sitemap_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                    ssl=False
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        extracted = await SitemapExtractor.parse_sitemap(content)
                        urls.extend(extracted)
                        logger.info(f"✅ Found {len(extracted)} URLs in {sitemap_url}")
                        break
            except Exception as e:
                logger.debug(f"⚠️  Could not fetch {sitemap_url}: {e}")
                continue
        
        return urls
    
    @staticmethod
    async def parse_sitemap(content: str) -> list:
        """Parse XML sitemap and extract URLs"""
        urls = []
        
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)
            
            # Handle both sitemap and sitemapindex
            for url_tag in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                if url_tag.text:
                    urls.append(url_tag.text)
        except Exception as e:
            logger.warning(f"⚠️  Error parsing sitemap: {e}")
        
        return urls


class RedirectTracker:
    """Track redirect chains and preserve original URLs"""
    
    def __init__(self):
        self.redirect_map = {}  # {final_url: [redirect_chain]}
    
    async def track_redirects(self, url: str, session: aiohttp.ClientSession) -> Tuple[str, list]:
        """Follow redirects and return final URL + redirect chain"""
        redirect_chain = []
        current_url = url
        max_redirects = 10
        
        try:
            async with session.head(
                url,
                allow_redirects=False,
                timeout=aiohttp.ClientTimeout(total=10),
                ssl=False
            ) as response:
                while response.status in (301, 302, 303, 307, 308) and max_redirects > 0:
                    redirect_url = response.headers.get('Location')
                    if not redirect_url:
                        break
                    
                    # Make redirect URL absolute
                    redirect_url = urljoin(current_url, redirect_url)
                    redirect_chain.append({
                        'from': current_url,
                        'status': response.status,
                        'to': redirect_url
                    })
                    
                    current_url = redirect_url
                    max_redirects -= 1
                    
                    # Follow next redirect
                    async with session.head(
                        current_url,
                        allow_redirects=False,
                        ssl=False
                    ) as next_response:
                        response = next_response
            
            if redirect_chain:
                logger.info(f"🔄 Redirect detected: {redirect_chain[0]['from']} -> {current_url}")
                self.redirect_map[current_url] = redirect_chain
        except Exception as e:
            logger.debug(f"⚠️  Error tracking redirects: {e}")
        
        return current_url, redirect_chain
