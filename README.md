# Web Crawler 🐍

Async web crawler optimized for AI model context (minimal tokens).

## Setup

```bash
git clone https://github.com/KomarovAI/web-crawler.git
cd web-crawler
pip install -r requirements.txt
cp .env.example .env
python crawler.py
```

## Config

Edit `.env`:
```
START_URL=https://example.com
MAX_PAGES=50
TIMEOUT=10
```

## API

```python
from crawler import Crawler
import asyncio

async def main():
    result = await Crawler('https://example.com', max_pages=100).run()
    print(f"Crawled {result['total']} pages")

asyncio.run(main())
```

## Tech

- Python 3.11+
- aiohttp (async HTTP)
- beautifulsoup4 (HTML parsing)
- python-dotenv (config)

## For AI Models

See `.github/AI_CONTEXT.txt` for compact project context (~250 tokens).
