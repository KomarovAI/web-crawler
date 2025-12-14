# Full Website Archiver

**Download complete websites with all images, CSS, JS, and convert links to local**

---

## Features

✅ **Complete download** - All HTML, CSS, JS, images  
✅ **Link rewriting** - Convert to local paths  
✅ **Organized structure** - Clean folder hierarchy  
✅ **Offline viewing** - Works without internet  
✅ **Asset deduplication** - Hash-based file names  
✅ **Relative links** - Navigation works in archive  
✅ **Database storage** - Indexed and searchable  

---

## Setup

### Install
```bash
pip install -r requirements.txt
cp .env.example .env
```

### Configure
```bash
START_URL=https://example.com
MAX_PAGES=20              # Limit pages (important!)
OUTPUT_DIR=site_archive  # Where to save
```

---

## Usage

### Basic
```bash
python crawler_full.py
```

### With custom config
```bash
START_URL=https://github.com MAX_PAGES=50 OUTPUT_DIR=github_archive python crawler_full.py
```

### Python API
```python
from crawler_full import FullCrawler
import asyncio

async def main():
    crawler = FullCrawler(
        u='https://example.com',
        m=20,
        out='my_archive'
    )
    result = await crawler.run()
    print(f"Downloaded {result['total']} pages")
    print(f"Location: {result['output']}")

asyncio.run(main())
```

---

## Output Structure

```
site_archive/
├── index.html               (Homepage)
├── about/
│   └── index.html
├── contact/
│   └── index.html
├── blog/
│   ├── index.html
│   ├── post-1/
│   │   └── index.html
│   └── post-2/
│       └── index.html
├── assets/                  (Images, CSS, JS)
│   ├── abc123def.jpg
│   ├── 456ghi789.css
│   ├── xyz123abc.js
│   └── ...
└── archive.db              (Database index)
```

---

## What Gets Downloaded

### HTML Pages
- ✅ All HTML pages found via crawling
- ✅ Saved as `/page/index.html`
- ✅ Links rewritten to local paths

### Assets (Auto-detected)
```html
<!-- Images -->
<img src="image.jpg">              → assets/hash.jpg

<!-- Stylesheets -->
<link rel="stylesheet" href="style.css"> → assets/hash.css

<!-- Scripts -->
<script src="app.js"></script>     → assets/hash.js

<!-- Media -->
<source src="video.mp4">           → assets/hash.mp4

<!-- Links -->
<a href="/page">                  → page/index.html
```

---

## Link Rewriting

### Before
```html
<img src="https://example.com/images/photo.jpg">
<link href="/static/style.css">
<a href="/about">
```

### After (Local)
```html
<img src="assets/abc123def.jpg">
<link href="assets/789ghi456.css">
<a href="../about/index.html">
```

### How It Works
1. Download all assets (images, CSS, JS)
2. Hash each file (MD5) → unique name
3. Rewrite all URLs in HTML
4. Save with relative paths
5. Works offline! 🌐➡️💾

---

## Database Schema

### pages table
```sql
SELECT url, local_path, ts FROM pages;

-- Example:
https://example.com        | index.html          | 1702643611.5
https://example.com/about  | about/index.html    | 1702643612.3
```

### assets table
```sql
SELECT url, type, length(data) as size FROM assets;

-- Example:
https://example.com/logo.png      | image/png       | 12345
https://example.com/style.css     | text/css        | 5678
https://example.com/app.js        | text/javascript | 34567
```

---

## Advanced Queries

### Find all images
```sql
SELECT url FROM assets WHERE type LIKE 'image/%';
```

### Find all stylesheets
```sql
SELECT url FROM assets WHERE type = 'text/css';
```

### Find all scripts
```sql
SELECT url FROM assets WHERE type = 'text/javascript';
```

### List all pages
```sql
SELECT url, local_path FROM pages ORDER BY ts DESC;
```

### Find large files
```sql
SELECT url, type, length(data) as size_bytes FROM assets 
WHERE length(data) > 1000000  -- > 1MB
ORDER BY size_bytes DESC;
```

---

## Viewing Archive

### Browser
```bash
# Open in browser
open site_archive/index.html      # macOS
xdg-open site_archive/index.html  # Linux
start site_archive/index.html     # Windows
```

### Local Server
```bash
# Python
cd site_archive
python -m http.server 8000
# Open http://localhost:8000

# Node
cd site_archive
npx http-server
```

### File Explorer
- Click `site_archive/index.html`
- Works offline (all links local)

---

## Performance

### Speed
```
Small site (10 pages):  5-10 seconds
Medium site (50 pages): 30-60 seconds
Large site (100 pages): 2-3 minutes

Limited by: Network speed, asset size, concurrent connections
```

### Storage
```
Small site (10 pages):   10-50 MB
Medium site (50 pages):  50-200 MB
Large site (100 pages):  200-500 MB

Depends on: Images, videos, media
```

### Concurrency
```
Default: 5 concurrent requests
Safe for: Most websites
Adjust: aiohttp.TCPConnector(limit=N)
```

---

## Common Use Cases

### 1. Backup Website
```python
await FullCrawler('https://mysite.com', m=100, out='backup').run()
# Creates complete offline backup
```

### 2. Offline Reading
```python
await FullCrawler('https://documentation.io', m=50, out='docs').run()
# Read documentation offline
```

### 3. Research Archive
```python
await FullCrawler('https://research.org', m=200, out='research').run()
# Archive research papers/content
```

### 4. Portfolio Demo
```python
await FullCrawler('https://portfolio.com', m=30, out='portfolio_demo').run()
# Show portfolio offline
```

---

## Limitations & Tips

### ⚠️ Limitations
- **JavaScript rendering** - No Puppeteer/Playwright (add if needed)
- **AJAX/dynamic content** - Won't load JavaScript-rendered content
- **Cookies/auth** - Can't handle login-required sites
- **Large sites** - Set reasonable MAX_PAGES limit
- **Rate limiting** - Some sites may block aggressive crawling

### ✅ Tips
- **Start small** - Test with MAX_PAGES=10 first
- **Be respectful** - Add delays, identify crawler
- **Check robots.txt** - Respect crawl directives
- **Use proxies** - For large-scale archiving
- **Filter domains** - Only download from target domain

---

## Troubleshooting

### "Missing images in offline version"
**Cause:** Site uses JavaScript to load images  
**Fix:** Need Playwright/Puppeteer version (future enhancement)

### "CSS not working"
**Cause:** Relative paths in CSS files  
**Fix:** Currently rewrites HTML links; CSS references may break  
**Workaround:** Download site from simple HTML structure

### "Too slow"
**Cause:** Too many pages or large assets  
**Fix:** Reduce MAX_PAGES or increase concurrency
```python
Fix: aiohttp.TCPConnector(limit=10)  # Increase from 5 to 10
```

### "Out of memory"
**Cause:** Downloading huge files to memory  
**Fix:** Stream large files to disk instead
```python
# Future: Add streaming support for large assets
```

### "Links broken"
**Cause:** External links rewritten  
**Fix:** Keep external links as-is (current behavior)

---

## Future Enhancements

### Priority 1
- [ ] CSS relative path rewriting
- [ ] JavaScript variable rewriting
- [ ] Form handling (local forms)
- [ ] Search functionality (full-text DB)

### Priority 2
- [ ] Playwright integration (JS rendering)
- [ ] Stream large files (memory-safe)
- [ ] Compression (.zip archive)
- [ ] Resume interrupted downloads

### Priority 3
- [ ] Diff detection (changed pages)
- [ ] Incremental updates
- [ ] Export to WARC format
- [ ] Web interface for browsing

---

## File Classes

### FullDB
```python
db = FullDB('archive.db')
db.save_asset(url, data, content_type)  # Save file
db.save_page(url, html, local_path)     # Save page
db.get_asset(url)                        # Retrieve file
```

### FullCrawler
```python
crawler = FullCrawler(
    u='https://example.com',  # Start URL
    m=50,                     # Max pages
    t=10,                     # Timeout
    out='site_archive'        # Output dir
)
await crawler.run()  # Execute
```

---

## Example: Complete Archive

```python
from crawler_full import FullCrawler
import asyncio
import webbrowser

async def main():
    print("📥 Downloading site...")
    crawler = FullCrawler(
        u='https://example.com',
        m=50,  # Limit to 50 pages
        out='example_archive'
    )
    result = await crawler.run()
    
    print(f"✅ Downloaded {result['total']} pages")
    print(f"📁 Location: {result['output']}")
    print(f"🌐 Opening in browser...")
    
    # Open in browser
    index = f"{result['output']}/index.html"
    webbrowser.open(f'file://{index}')

asyncio.run(main())
```

Run:
```bash
python example.py
# Downloads site + opens in browser
# Click around, everything works offline!
```

---

## Status

✅ **Full site archiving** - Working  
✅ **Asset downloading** - Working  
✅ **Link rewriting** - Working  
✅ **Database storage** - Working  
⚠️ **CSS rewriting** - Basic (paths may break)  
⚠️ **JavaScript rendering** - Not supported  
❌ **Authentication** - Not supported  

**Production ready for:** Simple HTML sites  
**May need enhancement for:** Complex JavaScript sites

---

**Next:** Try with your favorite site and explore offline! 🚀
