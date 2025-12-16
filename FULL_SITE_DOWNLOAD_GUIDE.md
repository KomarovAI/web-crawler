# 🔥 FULL-SITE DOWNLOAD GUIDE

## 🎉 WHAT'S NEW

Your crawler now **automatically downloads the complete website** (HTML + CSS + JS + Images) and saves it to SQLite database!

### Two-Phase Architecture:
```
🔥 PHASE 1: Download Full Website (httrack or wget)
           → Saves HTML, CSS, JS, images, fonts to DB

🐭 PHASE 2: Crawl & Extract (async Python)
           → Parse pages, extract assets, build links
```

---

## 📚 DATABASE STRUCTURE

### New Tables Added:

#### `downloaded_files` - All downloaded website files
```sql
CREATE TABLE downloaded_files (
    id INTEGER PRIMARY KEY,
    domain TEXT,              -- Domain crawled
    file_path TEXT,           -- Relative file path
    file_type TEXT,           -- 'html', 'css', 'js', 'image', 'font', 'other'
    file_size INTEGER,        -- File size in bytes
    content_hash TEXT,        -- SHA256 hash
    file_content BLOB,        -- 📇 ACTUAL FILE DATA
    url TEXT,                 -- Original URL
    downloaded_at TIMESTAMP
);
```

#### `download_metadata` - Download session info
```sql
CREATE TABLE download_metadata (
    domain TEXT PRIMARY KEY,
    tool_used TEXT,           -- 'httrack' or 'wget'
    start_url TEXT,           -- URL of the website
    download_start TIMESTAMP,
    download_end TIMESTAMP,
    total_files INTEGER,      -- How many files downloaded
    total_size INTEGER,       -- Total size in bytes
    success BOOLEAN,
    error_message TEXT
);
```

---

## 🚀 HOW IT WORKS

### Step 1: Install Download Tools
```bash
# Automatically done by GitHub Actions:
sudo apt-get install httrack wget
```

### Step 2: Run Crawler
```python
from smart_archiver_v2 import WARCCompliantArchiver

# Enable full-site download (default: True)
archiver = WARCCompliantArchiver(
    start_url='https://example.com',
    download_full_site=True  # 🔥 NEW parameter
)

await archiver.archive()
```

### Step 3: Access Downloaded Files
```python
from site_downloader_engine import SiteDownloaderEngine
import sqlite3

conn = sqlite3.connect('archive.db')
downloader = SiteDownloaderEngine(conn, 'example.com')

# Get a file
html_content = downloader.get_file('index.html')
css_content = downloader.get_file('css/style.css')
image_data = downloader.get_file('images/logo.png')

# Get statistics
stats = downloader.get_stats()
print(f"Total files: {stats['total_files']}")
print(f"Total size: {stats['total_size_mb']:.2f} MB")
print(f"By type: {stats['by_type']}")
```

---

## 💻 USAGE EXAMPLES

### Example 1: Download & Analyze Website
```python
import asyncio
from smart_archiver_v2 import WARCCompliantArchiver

async def download_site():
    archiver = WARCCompliantArchiver(
        start_url='https://callmedley.com',
        max_depth=5,
        max_pages=500,
        download_full_site=True
    )
    await archiver.archive()

asyncio.run(download_site())
```

### Example 2: Query Downloaded Files
```python
import sqlite3

conn = sqlite3.connect('archive.db')
cursor = conn.cursor()

# Get all HTML files
cursor.execute('''
    SELECT file_path, file_size FROM downloaded_files
    WHERE file_type = 'html'
    ORDER BY file_size DESC
    LIMIT 10
''')

for path, size in cursor.fetchall():
    print(f"{path}: {size/1024:.1f} KB")
```

### Example 3: Extract Downloaded CSS
```python
import sqlite3

conn = sqlite3.connect('archive.db')
cursor = conn.cursor()

# Get all CSS files
cursor.execute('''
    SELECT file_path, file_content FROM downloaded_files
    WHERE file_type = 'css'
''')

for path, content in cursor.fetchall():
    # Write to file
    with open(f'./extracted/{path}', 'wb') as f:
        f.write(content)
```

---

## 🔍 HOW TO RETRIEVE FILES FROM DATABASE

### Using SQLite CLI:
```bash
# Connect to database
sqlite3 archive.db

# List all downloaded files
SELECT file_path, file_type, file_size FROM downloaded_files LIMIT 20;

# Count by type
SELECT file_type, COUNT(*) FROM downloaded_files GROUP BY file_type;

# Get download metadata
SELECT * FROM download_metadata;
```

### Using Python:
```python
import sqlite3

conn = sqlite3.connect('archive.db')
cursor = conn.cursor()

# Get specific file
cursor.execute(
    'SELECT file_content FROM downloaded_files WHERE file_path = ?',
    ('index.html',)
)
html = cursor.fetchone()[0]

# Save to file
with open('index.html', 'wb') as f:
    f.write(html)
```

---

## 🏃 PERFORMANCE METRICS

### Download Speed (depends on internet):
- httrack: ~50-100 MB/min (highly optimized)
- wget: ~30-50 MB/min (conservative)

### Storage:
- HTML files: ~1-10 KB each
- CSS files: ~5-50 KB each
- Images: ~10 KB - 1 MB each
- Typical site: 100-500 MB in SQLite DB

### Database Compression:
- SQLite native: Good for text (HTML, CSS, JS)
- Artifacts: -80% with gzip compression

---

## 🔥 TOOLS USED

### httrack (Primary)
```bash
httrack https://example.com -O ./output -k -c16

# Features:
# -k: Convert links to local
# -c16: 16 concurrent threads
# -e: Save structure
```

### wget (Fallback)
```bash
wget --mirror --page-requisites --convert-links \
  --restrict-file-names=windows \
  -P ./output \
  https://example.com

# Features:
# --mirror: Mirror entire website
# --page-requisites: Download CSS, JS, images
# --convert-links: Convert to local links
```

---

## 📂 GITHUB ACTIONS INTEGRATION

### Automatic Installation:
```yaml
- name: 🔥 Install download tools (httrack + wget)
  run: |
    sudo apt-get update -qq
    sudo apt-get install -y -qq httrack wget
```

### Automatic Execution:
```yaml
- name: 🕷️ Run crawler + full-site download
  run: python smart_archiver_v2.py
```

### Verification:
Automatically checks:
- Downloaded files count
- Downloaded files size
- Files grouped by type

---

## 🏰 ARCHITECTURE

### File: `site_downloader_engine.py`
```python
class SiteDownloaderEngine:
    """🔥 Download full website using httrack/wget"""
    
    def check_tools()              # ✅ httrack or wget?
    async def download_site()      # Download & save to DB
    async def download_with_httrack()  # Using httrack
    async def download_with_wget() # Using wget (fallback)
    def get_file()                 # Retrieve file from DB
    def get_stats()                # Get download statistics
```

### Integrated in: `smart_archiver_v2.py`
```python
class WARCCompliantArchiver:
    # NEW:
    self.downloader = SiteDownloaderEngine(self.conn, domain)
    
    async def archive(self):
        # 🔥 PHASE 1: Full-site download
        if self.download_full_site:
            await self.downloader.download_site(url)
        
        # 🐭 PHASE 2: Crawl & extract
        # ... existing code ...
```

---

## 🔍 VERIFICATION SCRIPT

Automatic verification after download:

```yaml
- name: 🔍 COMPREHENSIVE VERIFICATION
  run: |
    python3 verify.py
```

Checks:
- ✅ Database integrity
- ✅ Downloaded files count
- ✅ Downloaded files size
- ✅ Files grouped by type
- ✅ HTML, CSS, JS, images present

---

## 🚀 FUTURE ENHANCEMENTS

### Planned:
1. **Resume interrupted downloads** - Cache-aware resuming
2. **Incremental downloads** - Only download changed files
3. **Compression per file** - gzip inside DB
4. **Export to static site** - Generate HTML files from DB
5. **Search index** - Full-text search across HTML
6. **Screenshot capture** - Headless browser screenshots
7. **JavaScript execution** - Render JS-generated content

---

## 💎 TROUBLESHOOTING

### Issue: "Neither httrack nor wget found!"
```bash
# Solution: Install manually
sudo apt-get install httrack wget
```

### Issue: Download too slow
```bash
# Use httrack (faster):
# Already set as primary tool, should use automatically
```

### Issue: Out of disk space
```bash
# Reduce max_pages or max_depth
archiver = WARCCompliantArchiver(
    start_url='https://example.com',
    max_depth=2,        # Reduce
    max_pages=100       # Reduce
)
```

### Issue: Some files not downloaded
```bash
# Check download_metadata table
sqlite3 archive.db
SELECT * FROM download_metadata;

# Check error_message field
```

---

## 🔗 API REFERENCE

### `SiteDownloaderEngine`

#### `__init__(conn, domain)`
- **conn**: SQLite connection
- **domain**: Domain name

#### `async download_site(url) -> dict`
- **url**: Website URL to download
- **Returns**: `{'success': bool, 'tool': str, 'files_processed': int}`

#### `get_file(file_path) -> bytes`
- **file_path**: Relative path to file
- **Returns**: File content as bytes

#### `get_stats() -> dict`
- **Returns**: `{'total_files': int, 'total_size_mb': float, 'by_type': dict}`

---

**Status:** ✅ **COMPLETE & READY** | **Integration:** Full crawler automation
