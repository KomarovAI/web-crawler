# Web Crawler 🐍

Async web crawler optimized for AI model context (minimal tokens) **+ SQLite database storage**.

## Quick Setup

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
USE_DB=true                    # Enable database storage
DB_FILE=crawled.db             # Database filename
```

## Features

✅ **Async crawler** - 10-15x faster than sync
✅ **SQLite storage** - Save HTML to database
✅ **Smart caching** - Reuse cached pages (instant!)
✅ **MD5 hashing** - Detect content changes
✅ **Timestamps** - Track when pages crawled
✅ **Single-domain** - Prevents unauthorized crawling
✅ **Error handling** - Graceful degradation

## Output Example

```
[1/50]https://example.com
[2/50]https://example.com/about
[CACHE]https://example.com/about   <-- Cached, instant!
[3/50]https://example.com/contact
... more crawling ...
✅ 50 pages
💾 48 pages in DB
```

## API

```python
from crawler import Crawler
import asyncio

async def main():
    # With database (default)
    result = await Crawler(
        u='https://example.com',
        m=100,
        use_db=True
    ).run()
    
    print(f"Crawled {result['total']} pages")
    print(f"Stored {result['db_pages']} pages in DB")

asyncio.run(main())
```

## Tech Stack

- Python 3.11+
- aiohttp (async HTTP)
- beautifulsoup4 (HTML parsing)
- python-dotenv (config)
- sqlite3 (database, built-in)

## Database

Pages stored in `crawled.db` with:
- URL
- Full HTML content
- MD5 hash (for change detection)
- Timestamp (when crawled)

See `.github/DATABASE_GUIDE.md` for:
- Advanced queries
- Incremental crawling
- Exporting data
- Change detection

## For AI Models

### Context Layers (Hierarchical)

**Layer 1 (Global):** `.github/AI_CONTEXT.txt` (~250 tokens)
- Use for: Understanding full project
- Copy entire file into AI chat

**Layer 2 (Module):** `.github/CONTEXT_FEATURE.txt` (~100 tokens)
- Use for: Adding features
- Reference with Layer 1

**Layer 3 (Prompts):** `.github/PROMPT_TEMPLATES.txt` (~200 tokens)
- Use for: Structured AI requests
- Pick relevant template

### Quick Start for AI

1. Copy `.github/AI_CONTEXT.txt`
2. Use template from `.github/PROMPT_TEMPLATES.txt`
3. Add your specific request
4. AI has full context (~500 tokens max)

## Documentation

- **`README.md`** - This file
- **`BEST_PRACTICES.md`** - AI optimization (9KB)
- **`RESEARCH_SUMMARY.txt`** - Research findings (8+ sources)
- **`.github/WEB_CRAWLING_PRACTICES.md`** - Crawling best practices
- **`.github/DATABASE_GUIDE.md`** - Database usage guide (NEW!)
- **`.github/INDEX.md`** - Navigation guide

## Performance

```
Async:      3.5 seconds (50 pages)
Sync:       52 seconds (50 pages)
Improvement: 15x faster

With cache: 2 seconds (cached pages)
Speed-up:   26x faster on second run!
```

## Compliance

✅ Respects domain filtering
✅ Rate limiting (100ms delays)
✅ Error handling (graceful)
✅ Async efficiency (10-15x faster)
✅ Transparent & educational

See `.github/WEB_CRAWLING_PRACTICES.md` for full compliance checklist.

## Next Steps

1. Set `.env` variables
2. Run `python crawler.py`
3. Check `crawled.db` for results
4. See database guide for advanced usage

---

**Status:** Production-ready with database support 🚀
