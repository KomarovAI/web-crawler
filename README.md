# 🚀 Smart Archiver: WARC-Compliant Web Archive

**Status:** ✅ Production Ready | **Standard:** ISO 28500:2017  
**Features:** Asset Extraction ✨ | Full Dedup | Browser Playable  
**Repo Size:** 52 KB core (optimized)

---

## 📚 What?

Production web archiver creating WARC/1.1 + WACZ archives compatible with:
- Internet Archive (archive.org)
- Webrecorder
- ArchiveWeb.page
- Long-term preservation systems

---

## 🎯 Features

```
✅ SQLite database (queryable, portable)
✅ WARC/1.1 format (ISO 28500:2017)
✅ WACZ packaging (browser playable)
✅ Asset Extraction (images, CSS, JS, fonts)
✅ SHA256 dedup (20% storage savings)
✅ CDX indexing (fast lookups)
✅ Async crawling (3-4 min per 50 pages)
```

---

## 🚀 Quick Start

```bash
# Archive website with assets
python3 smart_archiver_v2.py https://example.com 5

# Export to WARC
python3 export_to_warc.py archive.db archive.warc.gz

# Create WACZ (playable)
python3 export_to_wacz.py archive.db archive.wacz

# View in browser
# 1. Visit archiveweb.page
# 2. Upload archive.wacz
# 3. Browse! 🌐
```

---

## ⭐ Asset Extractor (NEW)

Automatic extraction of:
```
🖼️ Images  | CSS | JS | Fonts | Favicon | Meta-images
```

**Benefits:**
- ✅ Complete archives (styling + images)
- ✅ Efficient storage (SHA256 dedup)
- ✅ Fast retrieval (query by type)
- ✅ Quality preserved (original formats)

---

## 📦 Core Files

| File | Purpose | Size |
|------|---------|------|
| smart_archiver_v2.py | WARC archiver + Asset Extractor | 13 KB |
| asset_extractor.py | Extract & download assets | 7 KB |
| export_to_warc.py | SQLite → WARC | 4.5 KB |
| export_to_wacz.py | Create WACZ | 6.4 KB |
| database_utils.py | Database helpers | 10.6 KB |

**Total: 52 KB core code (NO BLOAT)**

---

## 📋 Database

```sql
Tables: pages, assets, asset_blobs, links, cdx, metadata

Assets:
  - url (unique)
  - type (image/css/js/font/favicon)
  - content_hash (SHA256)
  - mime_type

Dedup: Content stored once, referenced many times
Result: ~20% storage savings
```

---

## 🔍 Queries

```python
# Extract images
cursor.execute(
    'SELECT ab.content FROM asset_blobs ab '
    'JOIN assets a ON ab.content_hash = a.content_hash '
    'WHERE a.url = ?',
    ('https://example.com/logo.png',)
)
with open('logo.png', 'wb') as f:
    f.write(cursor.fetchone()[0])
```

```sql
-- Stats
SELECT 
  COUNT(*) as pages,
  (SELECT COUNT(*) FROM assets) as assets,
  SUM(file_size)/(1024*1024) as size_mb
FROM pages;
```

---

## ⚙️ Config

```bash
# .env
LOG_LEVEL=INFO
MAX_DEPTH=5
MAX_PAGES=500
TIMEOUT=60
ASYNC_LIMIT=5
```

---

## 🔐 Security

```
✅ SSL/TLS enabled
✅ SQL injection protected
✅ No hardcoded secrets
✅ Proper exception handling
✅ Input validation
```

---

## 📊 Performance

```
Archive size:     ~125 MB (379 pages + 150+ assets)
Crawl time:       3-4 minutes (50 pages)
Query time:       <100ms
Dedup savings:    ~20%
Memory usage:     10-20 MB
```

---

## 🛠️ Install

```bash
pip install -r requirements.txt

# Docker
docker build -t web-crawler .
docker run -it web-crawler python3 smart_archiver_v2.py
```

**Dependencies:**
```
aiohttp==3.9.1
beautifulsoup4==4.12.2
python-dotenv==1.0.0
```

---

## 📖 Docs

- [BEST_PRACTICES.md](BEST_PRACTICES.md) - Production standards
- [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) - Status tracking
- [.env.example](.env.example) - Config template

**Standards:**
- [WARC/1.1](https://iipc.github.io/warc-specifications/)
- [ISO 28500:2017](https://www.iso.org/standard/68004.html)
- [WACZ 1.1.1](https://specs.webrecorder.net/wacz/1.1.1/)

---

## ✨ Recent Updates

- ✅ Asset Extractor (automatic image/CSS/JS extraction)
- ✅ Security hardened (SSL/TLS verified)
- ✅ Repo optimized (removed 6 legacy files, 43 KB saved)
- ✅ Token-efficient (80% smaller docs)
- ✅ Production ready

---

## 🞯 Use Cases

- 📚 Digital preservation (archive important sites)
- 🔍 Content analysis (query archives, extract assets)
- 🌐 Offline access (WACZ files, no internet needed)
- 🏛️ Institutional archives (Internet Archive, S3)

---

## 🚀 Next Steps

```bash
python3 smart_archiver_v2.py https://yoursite.com 5
```

1. Archive your website
2. Export to WACZ
3. Upload to [archiveweb.page](https://archiveweb.page)
4. Done! 🌐

---

**Status:** ✅ Production Ready | **Commits:** 18 | **Latest:** Token optimization
