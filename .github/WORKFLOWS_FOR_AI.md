# 🤖 GitHub Actions Workflows - For AI Agents

**Purpose:** Automated website crawling via GitHub runners  
**Trigger:** Manual, scheduled, or API-based  
**Output:** WARC + WACZ archives (queryable)  
**Cost:** FREE (3000 min/month quota)

---

## 💡 Workflows Available

### 1. crawl-website.yml (Single Site)

```yaml
On demand trigger:
  - Manual: Actions tab → Run workflow
  - Scheduled: Daily 2 AM UTC
  - API: GitHub dispatch event

Input:
  TARGET_URL: https://example.com
  MAX_DEPTH: 5

Output:
  - archive.db (SQLite)
  - archive.warc.gz (ISO 28500:2017)
  - archive.wacz (browser-playable)
  - Release artifact

Runtime: 3-5 minutes
```

### 2. batch-crawl.yml (Multiple Sites)

```yaml
On demand trigger:
  - Manual with JSON array
  - Parallel execution (max 3)

Input JSON:
  [
    {"url": "site1.com", "depth": 5},
    {"url": "site2.com", "depth": 3},
    {"url": "site3.com", "depth": 4}
  ]

Output:
  - Combined archive.db
  - Summary report (JSON)
  - Release artifact

Runtime: 5-10 minutes
```

---

## 🚀 For AI Integration

### API Trigger (From AI Agent)

```bash
curl -X POST \
  https://api.github.com/repos/KomarovAI/web-crawler/dispatches \
  -H 'Authorization: token YOUR_GITHUB_TOKEN' \
  -H 'Accept: application/vnd.github.v3+json' \
  -d '{"event_type": "crawl-website"}'
```

### Check Status (From AI Agent)

```bash
curl https://api.github.com/repos/KomarovAI/web-crawler/actions/runs \
  -H 'Authorization: token YOUR_GITHUB_TOKEN' 
```

### Download Result (From AI Agent)

```bash
# Get latest release
curl https://api.github.com/repos/KomarovAI/web-crawler/releases/latest \
  | jq '.assets[0].browser_download_url'
```

---

## 💾 What Gets Stored

```
✅ SQLite database (.db) - Full crawl data
  - pages table (HTML content)
  - assets table (images, CSS, JS)
  - links table (relationships)
  - cdx index (fast lookups)
  - metadata

✅ WARC archive (.warc.gz) - ISO 28500:2017
  - Standard format
  - Compressible
  - Archival-grade

✅ WACZ package (.wacz) - Browser playable
  - Embed HTML viewer
  - All assets included
  - Shareable
```

---

## 📄 Query Archive (From AI)

```python
import sqlite3

conn = sqlite3.connect('archive.db')
c = conn.cursor()

# Get all pages
c.execute('SELECT url, title FROM pages')
for url, title in c.fetchall():
    print(f'{title}: {url}')

# Get images only
c.execute('SELECT url FROM assets WHERE asset_type="image"')
images = c.fetchall()

# Get by domain
c.execute('SELECT * FROM pages WHERE domain="example.com"')
pages = c.fetchall()
```

---

## ⌨️ Workflow Files Location

```
.github/workflows/
├── crawl-website.yml       (single site)
├── batch-crawl.yml         (multi site)
├── AI_CONTEXT.md           (this)
├── WORKFLOWS_FOR_AI.md     (this)
```

---

## 📊 Usage Examples

### Example 1: Manual Crawl

```
GitHub → Actions → crawl-website → Run workflow
✓ Wait 5 minutes
✓ Download archive.db
```

### Example 2: AI-Triggered Crawl

```python
import subprocess

# Trigger workflow
subprocess.run([
    'gh', 'workflow', 'run', 'crawl-website.yml',
    '-f', 'target_url=https://example.com',
    '-f', 'max_depth=5'
])
```

### Example 3: Scheduled Crawls

```yaml
# Already configured in crawl-website.yml
schedule:
  - cron: '0 2 * * *'  # Daily 2 AM UTC
```

---

## 🜟 AI Agent Workflow

```
① AI needs data
  ↓
② Trigger GitHub Actions workflow (API)
  ↓
③ Workflow runs in GitHub runner
  ↓
④ Crawler generates archive.db
  ↓
⑤ Archive uploaded to releases
  ↓
⑥ AI downloads archive.db
  ↓
⑦ AI queries SQLite
  ↓
⑧ AI analyzes data
```

---

## 🛠️ Configuration

### Set Environment (in workflow)

```yaml
env:
  TARGET_URL: ${{ github.event.inputs.target_url }}
  MAX_DEPTH: ${{ github.event.inputs.max_depth }}
  LOG_LEVEL: INFO
  ASYNC_LIMIT: 5
```

### Secrets (GitHub Settings)

```
- GITHUB_TOKEN (auto-provided)
- Custom secrets (if needed)
```

---

## ⚠️ Important Notes

```
✅ Workflows run ONLY in GitHub infrastructure
✅ No local installation required
✅ Free tier: 3000 min/month
✅ We use: ~150 min/month (~5%)
✅ Archives stored as GitHub Releases
✅ Released artifacts kept permanently
✅ Works 24/7 automatically
```

---

## 🌟 Next Steps for AI

1. Fork repository
2. Enable GitHub Actions
3. Create GitHub Personal Access Token
4. Use token in AI agent to trigger workflows
5. Download + analyze archives

---

**Status:** 🤖 AI-Ready | **Trigger:** API/Manual/Scheduled | **Runner:** GitHub Actions
