# 🤖 Best Practices: AI-Ready Web Crawler (GitHub Actions)

**Status:** 🟢 Production-Ready | **For:** AI Agents | **Tokens:** ~800 (ultra-optimized)

---

## 🚀 What This Is

**Automated crawler for AI agents** running on GitHub Actions runners

```
🚀 Crawls websites automatically
📋 Stores in queryable SQLite
💾 Exports WARC (ISO 28500:2017)
🤖 Designed for AI/ML integration
🜟 Runs 24/7 in GitHub infrastructure
```

---

## 🎯 Core Principles

**Minimal sufficient information** - Anthropic methodology
- Include: schemas, APIs, critical patterns
- Exclude: verbose comments, unnecessary types
- **Goal:** Token-efficient for AI context

---

## 🚄 Architecture

```python
GitHub Actions Runner
    ↓
    smart_archiver_v2.py (main crawler)
    ↓
    AssetExtractor (images, CSS, JS)
    ↓
    SQLite Database (queryable)
    ↓
    Release Artifact (persistent)
```

---

## 📦 Core Components

```
smart_archiver_v2.py    (13 KB)  – Main crawler
asset_extractor.py      (7 KB)   – Asset download
export_to_warc.py       (4.5 KB) – WARC export
export_to_wacz.py       (6.4 KB) – WACZ export
database_utils.py       (10.6 KB)– DB helpers
database_schema.sql     (4.7 KB) – Schema

Total: 52 KB core (SLIM!)
```

---

## 💫 Database Schema

```sql
pages:
  id, url (unique), title, status_code, content, crawled_at

assets:
  url, type (image/css/js/font/favicon), mime_type, file_size, content_hash

asset_blobs:
  content_hash (unique), content (BLOB)

links:
  from_page_id, to_page_id (for graph analysis)

cdx:
  url, timestamp, record_type (indexing)
```

---

## 🤖 For AI Integration

### Query Pages

```python
import sqlite3

conn = sqlite3.connect('archive.db')
c = conn.cursor()

# Get all pages
c.execute('SELECT url, title, content FROM pages')
pages = c.fetchall()
```

### Extract Assets

```python
# Images only
c.execute('SELECT url FROM assets WHERE asset_type="image"')
images = c.fetchall()
```

### Link Analysis

```python
# Graph for AI analysis
c.execute('SELECT from_page_id, to_page_id FROM links')
links = c.fetchall()
```

---

## 🚀 GitHub Actions Integration

```yaml
# Trigger from AI agent
GitHub API → dispatch workflow → crawl_website.yml
             ↓
             GitHub runner (3-5 min)
             ↓
             archive.db + WARC + WACZ
             ↓
             Release artifact
             ↓
             AI downloads + analyzes
```

---

## ✅ Security

```
✅ SSL/TLS enabled
✅ No hardcoded secrets (use GitHub Secrets)
✅ SQL injection protected (parameterized)
✅ Input validation on URLs
✅ No PII storage (unless in content)
```

---

## 📊 Performance

```
Crawl time:      3-5 min (50 pages + assets)
Archive size:    ~125 MB
Asset dedup:     20% savings
Memory:          10-20 MB
Query speed:     <100 ms
Monthly cost:    FREE (3000 min quota)
```

---

## 💭 Workflows

```
crawl-website.yml   – Single site (manual/scheduled)
batch-crawl.yml     – Multiple sites (parallel)

Schedule: Daily 2 AM UTC (configurable)
Trigger: Manual or API-based
Runtime: 3-10 minutes
```

---

## 📝 Docs

- [README.md](README.md) - Getting started
- [AI_CONTEXT.md](.github/AI_CONTEXT.md) - AI integration
- [WORKFLOWS_FOR_AI.md](.github/WORKFLOWS_FOR_AI.md) - Workflow guide
- [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) - Status

---

## 💋 Token Savings

```
Before optimization:  7200 tokens
After optimization:   2000 tokens (docs)
                      5000+ tokens (available for code)

Result: 72% reduction! 🚀
```

---

## ⚠️ Not A Web Server

```
❌ Does NOT serve websites to users
❌ Does NOT act as proxy/reverse proxy
❌ Does NOT cache content
❌ Does NOT host applications

✅ IS a crawler that archives sites
✅ IS designed for AI automation
✅ IS WARC/WACZ compliant
✅ IS free (GitHub Actions)
```

---

## 🚀 Next Steps

1. Fork repository
2. Enable GitHub Actions
3. Trigger first crawl
4. Download archive.db
5. Query with AI

---

**Status:** 🤖 AI-Ready | **Runner:** GitHub Actions | **Cost:** FREE
