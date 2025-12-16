# 🤖 AI Context Guide - GitHub Actions Web Crawler

**For:** AI agents, ML models, autonomous systems  
**Purpose:** Understand how this crawler works for AI integration  
**Tokens:** ~300 (ultra-compact)

---

## 🚀 Architecture

```
GitHub Actions Runner
    ↓
    smart_archiver_v2.py (main crawler)
    ↓
    AssetExtractor (images/CSS/JS/fonts)
    ↓
    SQLite Database (queryable)
    ↓
    export_to_warc.py (ISO 28500:2017)
    ↓
    Release Artifact (GitHub)
    ↓
    AI Agent (download + analyze)
```

---

## 📋 How AI Agents Use This

### 1. Trigger Crawl

```python
# AI agent triggers GitHub Actions
import requests

response = requests.post(
    'https://api.github.com/repos/KomarovAI/web-crawler/dispatches',
    headers={'Authorization': 'token YOUR_TOKEN'},
    json={'event_type': 'crawl-website'}
)
```

### 2. Monitor Progress

```python
# Check workflow status
workflow_runs = requests.get(
    'https://api.github.com/repos/KomarovAI/web-crawler/actions/runs'
).json()

if workflow_runs['workflow_runs'][0]['status'] == 'completed':
    print('Crawl finished!')
```

### 3. Download Archive

```python
# Get SQLite database
releases = requests.get(
    'https://api.github.com/repos/KomarovAI/web-crawler/releases'
).json()

db_url = releases[0]['assets'][0]['browser_download_url']
archive_data = requests.get(db_url).content
```

### 4. Query Database

```python
import sqlite3

conn = sqlite3.connect('archive.db')
cursor = conn.cursor()

# Get all pages
cursor.execute('SELECT url, title FROM pages')
for url, title in cursor.fetchall():
    print(f"{title}: {url}")

# Get images
cursor.execute(
    'SELECT url FROM assets WHERE asset_type = "image"'
)
images = cursor.fetchall()
```

---

## 💾 Data Schema

```sql
pages:              url, title, status_code, content, crawled_at
assets:             url, type, mime_type, file_size, content_hash
asset_blobs:        content_hash, content (BLOB)
links:              from_page_id, to_page_id
cdx:                url, timestamp, record_type
metadata:           key, value
```

---

## 🛣️ GitHub Actions Workflows

### crawl-website.yml

```yaml
Trigger: Manual or scheduled (daily 2 AM UTC)
Input: TARGET_URL, MAX_DEPTH
Output: archive.db, archive.warc.gz, archive.wacz
Time: 3-5 minutes
Cost: ~5 min/run (FREE)
```

### batch-crawl.yml

```yaml
Trigger: Manual
Input: JSON array of URLs
Output: Combined archive + report
Time: 5-10 minutes
Cost: ~10-15 min/run (FREE)
```

---

## 📄 API Reference

```python
class WARCCompliantArchiver:
    def __init__(self, start_url: str, db_path: str, 
                 max_depth: int = 5, max_pages: int = 500)
    async def archive(self) -> dict
    async def finalize(self) -> dict

class AssetExtractor:
    async def extract(self, html: str, base_url: str) -> list
    async def download_assets(self, urls: list) -> dict
```

---

## 🛶 Resource Limits

```
Memory:             512 MB (soft limit)
CPU:                2 cores
Disk:               GitHub Actions provides ~14 GB
Timeout:            360 minutes (6 hours)
```

---

## 🌟 AI Integration Patterns

### Pattern 1: Autonomous Crawler

```python
class AICrawler:
    def __init__(self, github_token: str):
        self.token = github_token
    
    async def crawl_website(self, url: str):
        # Trigger workflow
        # Wait for completion
        # Download + analyze
        pass
```

### Pattern 2: Batch Processing

```python
urls = ['site1.com', 'site2.com', 'site3.com']
# Upload JSON to GitHub
# Trigger batch workflow
# Wait 10 minutes
# Download combined archive
# Analyze all sites
```

### Pattern 3: Content Analysis

```python
# After crawl
conn = sqlite3.connect('archive.db')

# AI reads all pages
cursor.execute('SELECT content FROM pages')
for page in cursor:
    ai_model.analyze(page)
```

---

## ✨ Environment Variables

```bash
# GitHub Actions secrets
GITHUB_TOKEN          # Auto-provided by GitHub
TARGET_URL            # Website to crawl
MAX_DEPTH             # How deep (default: 5)
MAX_PAGES             # Max pages (default: 500)
LOG_LEVEL             # DEBUG/INFO/WARNING (default: INFO)
```

---

## 🛠️ Error Handling

```python
try:
    # Workflow fails gracefully
    # Logs available in Actions tab
    # Last successful archive still available
except Exception as e:
    # AI can check workflow status
    # Retry automatically
    pass
```

---

## 🔐 Security for AI

```
✅ GitHub Secrets (no exposed tokens)
✅ SSL/TLS enabled (secure crawling)
✅ No PII stored (unless in target site)
✅ Archive stored as release (persistent)
✅ Source code public (transparent)
```

---

## 📄 Example: AI Agent

```python
import asyncio
import sqlite3
import requests

class AIWebArchiver:
    def __init__(self, github_token):
        self.token = github_token
        self.headers = {'Authorization': f'token {github_token}'}
    
    async def crawl_and_analyze(self, url: str):
        # 1. Trigger workflow
        self._trigger_workflow(url)
        
        # 2. Wait for completion
        await asyncio.sleep(300)  # Wait 5 minutes
        
        # 3. Download archive
        db = self._download_latest_release()
        
        # 4. Analyze
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute('SELECT content FROM pages LIMIT 10')
        pages = cursor.fetchall()
        
        # 5. AI analysis
        for page in pages:
            self._analyze_with_ai(page)
    
    def _trigger_workflow(self, url):
        requests.post(
            'https://api.github.com/repos/KomarovAI/web-crawler/dispatches',
            headers=self.headers,
            json={'event_type': 'crawl-website'}
        )
    
    def _download_latest_release(self):
        # Download from GitHub Releases
        pass
    
    def _analyze_with_ai(self, content):
        # Your AI logic here
        pass

# Use it
agent = AIWebArchiver('your_github_token')
asyncio.run(agent.crawl_and_analyze('https://example.com'))
```

---

## 🔍 Useful Queries for AI

```sql
-- Pages by status
SELECT status_code, COUNT(*) FROM pages GROUP BY status_code;

-- Asset breakdown
SELECT asset_type, COUNT(*), SUM(file_size) FROM assets 
GROUP BY asset_type;

-- Crawl statistics
SELECT 
  COUNT(*) as total_pages,
  (SELECT COUNT(*) FROM assets) as total_assets,
  SUM(file_size)/(1024*1024) as size_mb
FROM pages;

-- Extract links for graph analysis
SELECT from_page_id, to_page_id FROM links;
```

---

**Status:** 🤖 AI-Ready | **Tokens:** 300 | **Purpose:** Autonomous crawling
