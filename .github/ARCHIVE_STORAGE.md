# 📦 WHERE ARCHIVES ARE STORED

**АРХИВЫ ХРАНЯТСЯ В ОДНОМ МЕСТЕ: GitHub Actions Artifacts**

---

## 🟢 GitHub Actions Artifacts (ГЛАВНОЕ)

### Путь доступа:
```
https://github.com/KomarovAI/web-crawler/actions
↓
Select workflow run
↓
"Artifacts" tab
↓
Download crawl-results
```

### Что там:
```
✅ archive.db          SQLite database (весь краул)
✅ archive.warc.gz     ISO 28500:2017 format
✅ archive.wacz        Browser-playable
✅ CRAWL_REPORT.md     Report о крауле
```

### Тип хранения:
```
⏱️  Время жизни: 90 дней (по умолчанию, можно менять)
📦 Размер: ~125 MB per archive
💾 Лимит: ~400 GB per repo
🔒 Видимость: Private to repo (только участники видят)
```

---

## 🔗 КАК СКАЧАТЬ

### Вариант 1: GitHub Web UI (Easiest)

```
1. https://github.com/KomarovAI/web-crawler
2. Actions tab (верхняя панель)
3. Select latest workflow run
4. "Artifacts" section
5. Click "crawl-results"
6. Download zip
7. Extract *.db / *.warc.gz / *.wacz
```

### Вариант 2: GitHub CLI

```bash
# List runs
gh run list --repo KomarovAI/web-crawler

# Download artifacts from latest run
gh run list --repo KomarovAI/web-crawler --limit 1 --json databaseId -q | head -1 | xargs -I {} gh run download {} --repo KomarovAI/web-crawler
```

### Вариант 3: GitHub API

```bash
# Get latest artifacts
curl https://api.github.com/repos/KomarovAI/web-crawler/actions/artifacts \
  -H "Authorization: token $GITHUB_TOKEN" | jq '.artifacts[] | {name, url: .archive_download_url}'
```

### Вариант 4: From AI Agent (Python)

```python
import requests
import os
import zipfile
from io import BytesIO

# Get latest artifacts
response = requests.get(
    'https://api.github.com/repos/KomarovAI/web-crawler/actions/artifacts',
    headers={'Authorization': f'token {os.environ["GITHUB_TOKEN"]}'}
)

artifacts = response.json()['artifacts']

if artifacts:
    artifact = artifacts[0]  # Latest
    
    # Download
    zip_url = artifact['archive_download_url']
    zip_data = requests.get(
        zip_url,
        headers={'Authorization': f'token {os.environ["GITHUB_TOKEN"]}'}
    ).content
    
    # Extract
    with zipfile.ZipFile(BytesIO(zip_data)) as z:
        z.extractall('.')
    
    # Query
    import sqlite3
    conn = sqlite3.connect('archive.db')
    c = conn.cursor()
    c.execute('SELECT url, title FROM pages LIMIT 10')
    pages = c.fetchall()
    print(pages)
```

---

## 📊 STORAGE HIERARCHY

```
GitHub Server
    ↓
    └─ Actions Tab
        └─ Workflow Runs
            └─ Artifacts (90 days)
                ├─ crawl-results
                │   ├─ *.db
                │   ├─ *.warc.gz
                │   ├─ *.wacz
                │   └─ CRAWL_REPORT.md
                └─ batch-summary (for batch crawls)
```

---

## 🔄 ЖИЗНЕННЫЙ ЦИКЛ АРХИВА

```
1. Trigger workflow
   ↓
2. GitHub runner starts
   ├─ /home/runner/work/web-crawler/web-crawler/ (temporary)
   ├─ Runs smart_archiver_v2.py
   ├─ Creates *.db / *.warc.gz / *.wacz
   └─ (~125 MB temp storage)
   ↓
3. Upload to Artifacts
   └─ actions/upload-artifact@v4
   ↓
4. Stored in GitHub Actions Artifacts
   ├─ 90 days retention (default)
   ├─ Visible in Actions tab
   ├─ Downloadable via UI/CLI/API
   └─ ~400 GB total limit per repo
   ↓
5. After 90 days
   └─ Automatically deleted
```

---

## 📋 WORKFLOW CONFIGURATION

### crawl-website.yml
```yaml
# Single site crawl
# Saves to: Artifacts (crawl-results)
# Retention: 90 days
# Manual + scheduled triggers

steps:
  - run: python3 smart_archiver_v2.py ...
  - uses: actions/upload-artifact@v4
    with:
      name: crawl-results
      path: |
        *.db
        *.warc.gz
        *.wacz
        CRAWL_REPORT.md
      retention-days: 90
```

### batch-crawl.yml
```yaml
# Multiple sites (parallel, max 3)
# Each site: separate artifact
# Saves to: Artifacts (batch-results-DOMAIN)
# Retention: 90 days
```

---

## ⚡ QUICK ACCESS

### Fastest way to get latest archive:

```bash
# Using GitHub CLI (simplest)
gh run list --repo KomarovAI/web-crawler --limit 1 --json databaseId -q | head -1 | xargs -I {} gh run download {} --repo KomarovAI/web-crawler --pattern "*.db"

# Or: GitHub web UI
# 1. Actions tab
# 2. Latest run
# 3. Artifacts → crawl-results → Download
```

---

## 🔍 VIEW IN GITHUB WEB

```
https://github.com/KomarovAI/web-crawler/actions
                                         ↑ Click here
                                         
→ Workflows
→ Latest run
→ Artifacts
→ crawl-results (ZIP)
→ Extract & query with sqlite3
```

---

## 📊 RETENTION POLICY

```
⏱️  Default: 90 days
🔧 Can change in workflow:
   retention-days: 7    (shorter)
   retention-days: 365  (longer)
   retention-days: 1    (delete immediately)
```

---

## ✅ SUMMARY

| Where | Size | Time | Access | Cost |
|-------|------|------|--------|------|
| **Artifacts** | 125 MB | 90 days | Web/CLI/API | FREE |
| Runner disk | 125 MB | Minutes | Local only | Temp |
| Releases | - | FOREVER | - | Old way |

**→ YOU USE: Artifacts (not Releases!)**

---

## 🚀 FOR AI AGENTS

```python
# AI can download latest archive:
import os
import requests
import zipfile
from io import BytesIO
import sqlite3

token = os.environ['GITHUB_TOKEN']

# Get latest artifacts
resp = requests.get(
    'https://api.github.com/repos/KomarovAI/web-crawler/actions/artifacts',
    headers={'Authorization': f'token {token}'}
)
artifacts = resp.json()['artifacts']

if artifacts:
    # Download latest
    url = artifacts[0]['archive_download_url']
    zip_data = requests.get(url, headers={'Authorization': f'token {token}'}).content
    
    # Extract & query
    with zipfile.ZipFile(BytesIO(zip_data)) as z:
        z.extractall()
    
    conn = sqlite3.connect('archive.db')
    c = conn.cursor()
    c.execute('SELECT * FROM pages')
    # AI analysis here
```

---

**STATUS:** 🟢 All archives in GitHub Actions Artifacts  
**RETENTION:** 90 days (configurable)  
**ACCESS:** Web UI, CLI, API, or programmatically  
**COST:** FREE
