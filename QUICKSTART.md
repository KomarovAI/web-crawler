# Quick Start 🚀

## 1–5 Min Setup

```bash
# Clone & setup
git clone https://github.com/KomarovAI/web-crawler.git
cd web-crawler
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env: SET START_URL=https://your-domain.com

# Run
python crawler.py
```

## Docker

```bash
docker-compose up
```

## Output

```
[1/50] https://example.com
[2/50] https://example.com/about
[3/50] https://example.com/contact
...
✅ Crawled 15 pages
```

## Configuration (.env)

```
START_URL=https://example.com      # Starting page
MAX_PAGES=50                        # Max pages to crawl
TIMEOUT=10                          # Request timeout (sec)
```

## Customization

### Increase speed
```python
# In crawler.py, line ~42:
connector = aiohttp.TCPConnector(limit=10)  # was 5
```

### More debug info
```python
# In crawler.py, line ~47:
print(f"[{len(self.visited)}/{self.max_pages}] {url} - {len(html)} bytes")
```

### Save results
```python
# In crawler.py, line ~65:
with open('results.txt', 'w') as f:
    f.write('\n'.join(result['urls']))
```

## Troubleshooting

**ModuleNotFoundError: No module named 'aiohttp'**
```bash
pip install -r requirements.txt
```

**SSL certificate error**
```python
# In crawler.py, line ~39:
async with session.get(url, ssl=False) as resp:
```

**Timeout issues**
```bash
# Edit .env:
TIMEOUT=30  # increase from 10
```

## API Usage

```python
import asyncio
from crawler import Crawler

async def main():
    crawler = Crawler(
        start_url='https://example.com',
        max_pages=100,
        timeout=15
    )
    result = await crawler.run()
    print(f"Crawled {result['total']} pages")
    print(result['urls'])

asyncio.run(main())
```

## Next Steps

- 🔍 See `AI_INTEGRATION.md` for AI model setup
- 📄 See `PROMPTS.md` for AI prompts
- 🪨 See `README.md` for full docs
