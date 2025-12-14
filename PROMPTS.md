# Prompts for AI Models 🤖

Готовые промпты для работы с этим проектом.

## Code Review Prompt

```
Analyze this web crawler project:
- Focus: performance, security, type hints
- Files: crawler.py, config.py, requirements.txt
- Report: bugs, improvements, best practices
- Output: concise list with examples

Project context:
- Async Python crawler with aiohttp
- Single-domain crawling, max_pages limit
- Minimal dependencies (3 packages only)
- Production-ready, typed
```

## Feature Request Prompt

```
Extend the crawler with new feature:
[DESCRIBE FEATURE]

Constraints:
- Keep code <150 lines
- No new external dependencies
- Maintain existing API (async methods)
- Add type hints
- Include error handling

Project summary: async web crawler, ~140 lines, aiohttp + BeautifulSoup
```

## Bug Fix Prompt

```
Fix this issue in crawler.py:
[PASTE ERROR/ISSUE]

Context:
- Crawler class with async fetch/parse/run methods
- Queue-based BFS traversal
- Domain limitation, visited set, max_pages check

Requirements:
- Minimal code change
- Keep async pattern
- Add logging if needed
- Test case description
```

## Optimization Prompt

```
Optimize this crawler for speed:
- Current: sequential URL fetching
- Goal: parallel requests, faster crawling
- Constraint: stay within aiohttp

Existing structure:
- TCPConnector with limit=5
- Single asyncio.sleep(0.1)
- fetch() and parse() are async

Propose: changes only, not full rewrite
```

## Testing Prompt

```
Create unit tests for web crawler:
- Mock aiohttp responses
- Test URL validation
- Test parsing links
- Test domain limitation

Framework: pytest + pytest-asyncio
Files to test: crawler.py
Keep it <50 lines
```

## Minimal Context Copy-Paste

### For Quick Questions

```
Web Crawler (Python async)
- Main: crawler.py (async Crawler class)
- Methods: fetch(url), parse(html), run()
- Config: START_URL, MAX_PAGES, TIMEOUT
- Tech: aiohttp, BeautifulSoup4
```

### For Code Changes

```
## Current crawler.py structure:

class Crawler:
    __init__(start_url, max_pages, timeout)
    _extract_domain(url) -> str
    _is_valid_url(url) -> bool
    async fetch(session, url) -> str|None
    async parse(html, base_url) -> list[str]
    async run() -> dict

## Key behavior:
- BFS queue-based traversal
- Single domain only
- Visited set prevents duplicates
- Async with TCPConnector(limit=5)
```

## Integration Template

When working with AI on this project:

1. **Context** - Copy relevant `## Current crawler.py structure`
2. **Request** - Specific task (feature/bug/optimize)
3. **Constraints** - Keep minimal deps, async pattern
4. **Format** - Code only, no explanation first
5. **Validation** - Check it matches existing style

## Token Counter Reference

```
crawler.py:           ~420 tokens
config.py:            ~40 tokens
requirements.txt:     ~10 tokens
docker setup:         ~30 tokens
TOTAL (core):         ~500 tokens

Tip: Always request minimal changes, not full rewrites
```

## Common Requests

| Task | Prompt Start |
|------|------------|
| Add feature | "Extend the crawler with..." |
| Fix bug | "Fix this issue in crawler.py..." |
| Optimize | "Optimize this crawler for..." |
| Review | "Analyze this web crawler..." |
| Test | "Create unit tests for..." |
| Document | "Write docstring for..." |

## Pro Tips 📌

✅ Always paste only the relevant file sections
✅ Use "Minimal Context" above for first message
✅ Request diff/patch format, not full file
✅ Specify constraints (token count, lines, deps)
✅ For multiple changes: separate requests
✅ Keep project token budget under 1000
