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

### Context Layers (Hierarchical)

**Layer 1 (Global):** `.github/AI_CONTEXT.txt` (~250 tokens)
- Use for: Understanding full project
- When: First contact, refactoring, architecture
- Copy entire file into AI chat

**Layer 2 (Module):** `.github/CONTEXT_FEATURE.txt` (~100 tokens)
- Use for: Adding features to crawler.py
- When: Feature additions, extensions
- Reference with Layer 1

**Layer 3 (Prompts):** `.github/PROMPT_TEMPLATES.txt`
- Use for: Structured AI requests
- Templates for: Features, bugs, optimization, review, integration
- Constraints built-in

### Quick Start for AI

1. Copy `.github/AI_CONTEXT.txt`
2. Paste into your AI chat
3. Use template from `.github/PROMPT_TEMPLATES.txt`
4. Add your specific request
5. AI has full context (~500 tokens max)

### Best Practices

See `BEST_PRACTICES.md` for industry-standard approaches:
- Context engineering (Anthropic)
- Token optimization (GitHub Models)
- Prompt engineering (Augment Code)
- Hierarchical layers (VS Code)

### Research

See `RESEARCH_SUMMARY.txt` for detailed findings from 8+ sources.
