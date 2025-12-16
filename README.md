# 🤖 Web Crawler for AI Agents (GitHub Actions)

**Purpose:** 🧠 AI/ML agents archive websites via GitHub Actions runners  
**Status:** ✅ Production Ready | **Standard:** ISO 28500:2017  
**Auto-Execute:** GitHub Actions scheduled crawls | **Output:** WARC + WACZ  

⚠️ **THIS IS A CRAWLER FOR AI AGENTS, NOT A WEB HOSTING PLATFORM**

---

## 🎯 What This Does

✅ **Automated website crawling** via GitHub Actions runners  
✅ **Creates WARC archives** (ISO 28500:2017 compliant)  
✅ **Extracts assets** (images, CSS, JS, fonts)  
✅ **Generates WACZ** (browser-playable packages)  
✅ **Stores in SQLite** (queryable database)  
✅ **Zero manual intervention** - scheduled + on-demand  
**✅ NEW:** **⚡ Ultra-fast website downloader (HTTrack, WGET, Monolith)**  

❌ **NOT:** Web server, hosting platform, or reverse proxy  
❌ **NOT:** For serving websites to users  
❌ **NOT:** A cache/CDN  

---

## 🚀 NEW: ULTIMATE WEBSITE DOWNLOADER

### 🔥 Download ANY website in 30 seconds!

#### Quick Examples:

```bash
# HTTrack (recommended - maximum control)
httrack https://callmedley.com -O ./site -k -%e -c16 --max-rate=0

# WGET (built-in - ultra-fast)
wget -m -p -k --domains callmedley.com --no-parent https://callmedley.com/

# Monolith (single file - easy sharing)
monolith https://callmedley.com/ -o site.html

# Docker (no installation needed)
docker run -v $(pwd)/downloads:/app/downloads downloader \
  download https://callmedley.com httrack

# Python module
python3 downloader/site_downloader.py https://callmedley.com -m all

# CLI Script
./downloader/cli.sh download https://callmedley.com all
```

### 📚 Three Powerful Engines

| Engine | Speed | Control | Install | Best For |
|--------|-------|---------|---------|----------|
| **HTTrack** ⭐ | ⚡⚡⚡⚡ | ⚡⚡⚡⚡⚡ | `brew install` | Maximum control + offline |
| **WGET** ⚡ | ⚡⚡⚡⚡⚡ | ⚡⚡⚡ | Built-in | Raw speed |
| **Monolith** 📦 | ⚡⚡⚡ | ⚡ | `brew install` | Single HTML file |

### 🎁 Includes Everything

✅ CLI script (bash)  
✅ Python module  
✅ Docker container  
✅ GitHub Actions workflow  
✅ Full documentation  

👉 **[START HERE: downloader/QUICKSTART.md](downloader/QUICKSTART.md)**  
📖 **[FULL DOCS: downloader/README.md](downloader/README.md)**  

---

## 🚀 How It Works (Crawler)

### Via GitHub Actions (Automated)

```yaml
# Scheduled daily at 2 AM UTC
# Crawls configured websites
# Generates archives automatically
# Stores artifacts for 90 days
```

### Via CLI (Manual)

```bash
python3 smart_archiver_v2.py https://example.com 5
```

---

## 🤖 For AI Agents

This repo is **AI-agent-friendly**:

```
✅ Token-optimized docs (2000 tokens)
✅ Modular code (easy to fork/extend)
✅ Clear API (simple Python interface)
✅ Well-documented (easy to understand)
✅ Production-ready (battle-tested)
✅ Downloader module (ultra-fast site extraction)
```

**Use Case:** Train AI to crawl, archive, download, and analyze websites autonomously.

---

## ⚡ GitHub Actions Runner Features

```
✅ Scheduled crawls (daily, weekly, custom)
✅ On-demand manual triggers
✅ Parallel multi-site crawling
✅ Auto-generated releases
✅ Artifact storage (90 days)
✅ Free tier: 3000 min/month (we use ~150 min)
✅ Website downloads via workflow
```

### Example: Daily Archive

```bash
# Every day at 2 AM UTC
# Crawls example.com (5 levels deep)
# Creates archive.db (~125 MB)
# Exports to WARC + WACZ
# Stores as release artifact
```

---

## 📦 Core (52 KB Slim Code)

| File | Purpose | For AI |
|------|---------|--------|
| smart_archiver_v2.py | Main crawler | Easy to fork/customize |
| asset_extractor.py | Asset download | Modular, reusable |
| export_to_warc.py | Format conversion | Standard output |
| export_to_wacz.py | Playable package | Shareable archive |
| database_utils.py | DB helpers | Query interface |
| **downloader/** | **New: Fast downloader** | **3 engines, CLI + Python** |

---

## 🚀 Quick Start (For AI Automation)

### 1. Fork This Repo

```bash
git clone https://github.com/YOUR-USERNAME/web-crawler
cd web-crawler
```

### 2. Configure GitHub Secrets

```bash
# .github/workflows/crawl-website.yml
env:
  TARGET_URL: https://your-site.com
  MAX_DEPTH: 5
```

### 3. Enable Actions

```
Settings → Actions → Allow all actions → Save
```

### 4. Trigger Crawl

```
Actions → crawl-website → Run workflow
```

### 5. Download Archive

```
Releases → Latest → Download archive.db / .wacz
```

---

## 🧠 API for AI Agents

```python
from smart_archiver_v2 import WARCCompliantArchiver
import asyncio

async def crawl_for_ai(url: str):
    archiver = WARCCompliantArchiver(
        start_url=url,
        db_path='archive.db',
        max_depth=5,
        max_pages=500
    )
    await archiver.archive()
    return 'archive.db'

# Use in AI agent
db = asyncio.run(crawl_for_ai('https://example.com'))
```

### Download Sites Programmatically

```python
from downloader.site_downloader import SiteDownloader

# Fast download with Python
downloader = SiteDownloader()
result = downloader.download('https://example.com', method='httrack')
# Or use all three methods
results = downloader.download_all('https://example.com')
```

---

## 💾 Outputs

```
archive.db        SQLite (queryable by AI)
archive.warc.gz   ISO 28500:2017 standard
archive.wacz      Browser-playable
downloads/        Full website copies (HTTrack/WGET)
site.html         Single-file archive (Monolith)
```

**For AI:** Query SQLite directly

```sql
SELECT url, title FROM pages WHERE domain = 'example.com';
SELECT url, asset_type FROM assets WHERE asset_type = 'image';
```

---

## 🔐 Security

✅ SSL/TLS enabled (no MITM)  
✅ No secrets in repo (use GitHub Secrets)  
✅ No hardcoded credentials  
✅ Input validation on URLs  
✅ SQL injection protected  

---

## 📊 Performance

```
Crawl time:      3-4 minutes (50 pages + assets)
Download time:   1-5 minutes (full site with HTTrack)
Archive size:    ~125 MB
Asset dedup:     20% storage savings
Memory:          10-20 MB
Query speed:     <100ms
```

---

## 🔧 For AI Development

### Fork & Customize

```bash
# Add AI-specific features
git checkout -b feature/ai-analysis

# Example: Add sentiment analysis to crawled content
# Example: Add NLP entity extraction
# Example: Add image classification
```

### Extend API

```python
# Add to smart_archiver_v2.py
class AIArchiver(WARCCompliantArchiver):
    async def analyze_content(self):
        # AI analysis here
        pass
```

---

## 📖 Docs

- [🚀 DOWNLOADER QUICKSTART](downloader/QUICKSTART.md) - **30 seconds to download any site**
- [📚 DOWNLOADER FULL DOCS](downloader/README.md) - Complete documentation
- [BEST_PRACTICES.md](BEST_PRACTICES.md) - Architecture
- [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) - Tracking
- [.env.example](.env.example) - Config

---

## ✨ Tech Stack

```
Python 3.11+
aiohttp (async HTTP)
beautifulsoup4 (HTML parsing)
SQLite3 (database)
Docker (containerization)
GitHub Actions (CI/CD)

✅ NEW: HTTrack, WGET, Monolith (downloaders)
```

---

## ⏱️ GitHub Actions Usage

```
Free tier:  3000 min/month
Our usage:  ~150 min/month (5%)
Cost:       FREE
```

---

## ⚠️ Important: This Is NOT

```
❌ Web server (doesn't serve content)
❌ Reverse proxy (not a middleman)
❌ Web hosting (archives only, no live serving)
❌ API provider (internal use only)
❌ Content delivery (for archival, not distribution)
```

**It's a crawler that runs in GitHub infrastructure + fast local downloader.**

---

## 🚀 Next Steps

1. **Quick download?** → [downloader/QUICKSTART.md](downloader/QUICKSTART.md)
2. Fork the repo
3. Enable GitHub Actions
4. Configure target URL
5. Run automated crawls
6. Download sites locally
7. Integrate with your AI agent
8. Analyze archives

---

**Status:** ✅ Production Ready | **For:** AI Agents | **Via:** GitHub Actions + Local Downloader  
**Repo Size:** 60 KB total | **Code:** 52 KB slim | **Docs:** Token-optimized  
**NEW:** ⚡ **Downloader module with 3 powerful engines (HTTrack, WGET, Monolith)**
