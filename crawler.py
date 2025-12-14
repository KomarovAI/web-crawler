#!/usr/bin/env python3
import asyncio
import os
from datetime import datetime
from urllib.parse import urljoin
from typing import Set

import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

class Crawler:
    def __init__(self, start_url: str, max_pages: int = 50, timeout: int = 10):
        self.start_url = start_url
        self.max_pages = max_pages
        self.timeout = timeout
        self.visited: Set[str] = set()
        self.queue = [start_url]
        self.domain = self._extract_domain(start_url)

    def _extract_domain(self, url: str) -> str:
        from urllib.parse import urlparse
        return urlparse(url).netloc

    def _is_valid_url(self, url: str) -> bool:
        if url in self.visited or len(self.visited) >= self.max_pages:
            return False
        if self._extract_domain(url) != self.domain:
            return False
        return url.startswith(('http://', 'https://'))

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> str | None:
        try:
            async with session.get(url, timeout=self.timeout, allow_redirects=True) as resp:
                if resp.status == 200 and 'text/html' in resp.headers.get('content-type', ''):
                    return await resp.text()
        except Exception:
            pass
        return None

    async def parse(self, html: str, base_url: str) -> list[str]:
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            url = urljoin(base_url, a['href'])
            if self._is_valid_url(url):
                links.append(url)
        return links

    async def run(self) -> dict:
        connector = aiohttp.TCPConnector(limit=5, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            while self.queue and len(self.visited) < self.max_pages:
                url = self.queue.pop(0)
                if url in self.visited:
                    continue

                self.visited.add(url)
                print(f"[{len(self.visited)}/{self.max_pages}] {url}")

                html = await self.fetch(session, url)
                if html:
                    links = await self.parse(html, url)
                    self.queue.extend(links)
                await asyncio.sleep(0.1)

        return {"total": len(self.visited), "urls": sorted(self.visited)}

async def main():
    url = os.getenv('START_URL', 'https://example.com')
    max_pages = int(os.getenv('MAX_PAGES', 50))
    result = await Crawler(url, max_pages).run()
    print(f"\n✅ Crawled {result['total']} pages")

if __name__ == '__main__':
    asyncio.run(main())
