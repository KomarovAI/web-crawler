# 📦 WHERE ARCHIVES ARE STORED

**АРХИВЫ ХРАНЯТСЯ В ТРЁХ МЕСТАХ:**

---

## 1️⃣ GitHub Releases (ГЛАВНОЕ)

### Путь:
```
https://github.com/KomarovAI/web-crawler/releases
```

### Что там:
```
✅ archive.db          SQLite database (весь краул)
✅ archive.warc.gz     ISO 28500:2017 format
✅ archive.wacz        Browser-playable
✅ CRAWL_REPORT.md     Отчёт о краулинге
```

### Как скачать:

```bash
# Via GitHub CLI
gh release list --repo KomarovAI/web-crawler
gh release download --repo KomarovAI/web-crawler

# Via curl
curl -L https://api.github.com/repos/KomarovAI/web-crawler/releases/latest \
  | jq '.assets[] | .browser_download_url' \
  | xargs -I {} curl -L {} -O

# Via browser
https://github.com/KomarovAI/web-crawler/releases/latest
```

### Тип хранения:
```
⏱️  Постоянное (FOREVER)
📦 Размер: ~125 MB per archive
💾 Лимит: Не ограничен
🔐 Видимость: Public (если репо public)
```

---

## 2️⃣ GitHub Actions Artifacts (ВРЕМЕННОЕ)

### Путь:
```
Settings → Actions → General → Artifact and log retention
Дефолт: 90 дней
```

### Что там:
```
📊 Промежуточные файлы
🔄 Logs from workflow
📈 Build metrics
```

### Как получить:

```bash
# Via GitHub Actions UI
1. Actions tab
2. Select workflow run
3. "Artifacts" section
4. Download

# Via GitHub CLI
gh run list --repo KomarovAI/web-crawler
gh run download {run-id} --repo KomarovAI/web-crawler
```

### Тип хранения:
```
⏱️  Временное (90 дней по умолчанию)
📦 Размер: ~125 MB per artifact
💾 Лимит: ~400 GB per repo
🔐 Видимость: Private to repo
```

---

## 3️⃣ GitHub Runner Disk (РАБОЧЕЕ ПРОСТРАНСТВО)

### Путь (во время краулинга):
```
/home/runner/work/web-crawler/web-crawler/
```

### Структура:
```
📂 /home/runner/work/web-crawler/web-crawler/
   ├── *.db              ← SQLite database (ПОКА КРАУЛИМ)
   ├── *.warc.gz         ← WARC archive (ПОКА ЭКСПОРТИРУЕМ)
   ├── *.wacz            ← WACZ package (ПОКА СОЗДАЁМ)
   ├── .env              ← Configuration (временно)
   ├── smart_archiver_v2.py
   ├── asset_extractor.py
   └── ...
```

### Тип хранения:
```
⏱️  Рабочее (во время workflow execution)
📦 Размер: ~125 MB for database
💾 Лимит: ~14 GB per runner
🔐 Видимость: Only during job
```

### Что происходит:
```
1. Workflow starts
   ↓
2. Repo cloned to /home/runner/work/...
   ↓
3. Crawler runs (creates .db)
   ↓
4. Export to .warc.gz and .wacz
   ↓
5. Upload to GitHub Releases
   ↓
6. Upload artifacts (90 days)
   ↓
7. Runner disk cleaned up
   ↓
8. ARCHIVES LIVE FOREVER in Releases ✅
```

---

## 🗂️ ХРАНИЛИЩЕ СТРУКТУРА

```
GitHub Server (cloud.github.com)
    ↓
    ├── 🟢 Releases (ПОСТОЯННОЕ)
    │   ├── archive.db (125 MB)
    │   ├── archive.warc.gz (125 MB)
    │   ├── archive.wacz (125 MB)
    │   └── CRAWL_REPORT.md
    │
    ├── 🟡 Actions Artifacts (90 дней)
    │   ├── Logs
    │   ├── Metrics
    │   └── Intermediate files
    │
    └── 🟠 Runner Disk (Временное)
        └── Cleared after workflow
```

---

## 📊 ДАННЫЕ ПО ХРАНЕНИЮ

| Место | Размер | Время жизни | Доступ | Лимит |
|-------|--------|-------------|--------|-------|
| **Releases** | 125 MB | FOREVER ✅ | Public | ∞ |
| **Artifacts** | 125 MB | 90 дней | Private | 400 GB |
| **Runner disk** | 125 MB | Few minutes | Local | 14 GB |

---

## 🔍 КАК НАЙТИ АРХИВЫ

### Вариант 1: GitHub Web UI

```
1. https://github.com/KomarovAI/web-crawler
2. Releases (right sidebar)
3. Latest release
4. Download archive.db
```

### Вариант 2: GitHub API

```bash
# Get latest release
curl https://api.github.com/repos/KomarovAI/web-crawler/releases/latest

# Get asset download URL
curl https://api.github.com/repos/KomarovAI/web-crawler/releases/latest \
  | jq '.assets[] | select(.name=="archive.db") | .browser_download_url'
```

### Вариант 3: GitHub CLI

```bash
# List releases
gh release list --repo KomarovAI/web-crawler

# Download latest
gh release download latest --repo KomarovAI/web-crawler
```

### Вариант 4: From AI Agent

```python
import requests
import sqlite3

# Get latest release
response = requests.get(
    'https://api.github.com/repos/KomarovAI/web-crawler/releases/latest'
)
release = response.json()

# Find archive.db
for asset in release['assets']:
    if asset['name'] == 'archive.db':
        url = asset['browser_download_url']
        
        # Download
        db_data = requests.get(url).content
        
        # Save and query
        with open('archive.db', 'wb') as f:
            f.write(db_data)
        
        # Query
        conn = sqlite3.connect('archive.db')
        c = conn.cursor()
        c.execute('SELECT url, title FROM pages LIMIT 10')
        pages = c.fetchall()
```

---

## ⚠️ ВАЖНО: ГДЕ КРАУЛЕР РАБОТАЕТ

```
Локально?        ❌ НЕТ
На сервере?      ❌ НЕТ
На GitHub?       ✅ ДА (GitHub Actions runner)
В Docker?        ✅ МОЖНО (если включить)

ЗАУСК ПРОЦЕССА:
1. Trigger workflow (manual/scheduled)
2. GitHub Actions allocates runner
3. Runner downloads repo
4. Runs smart_archiver_v2.py
5. Generates archives
6. Uploads to Releases
7. Runner destroyed
```

---

## 💾 ПЕРИОДИЧНОСТЬ КРАУЛИНГА

```
Scheduled crawl:  Daily 2 AM UTC (configurable)
On-demand:        Manual trigger via Actions tab
From AI:          Trigger via GitHub API

Все архивы сохраняются в Releases!
```

---

## 🎯 QUICK ACCESS

```bash
# Fastest way to get latest archive
gh release download latest \
  --repo KomarovAI/web-crawler \
  --pattern "*.db"

# Or direct curl
curl -L $(curl https://api.github.com/repos/KomarovAI/web-crawler/releases/latest \
  | jq -r '.assets[] | select(.name=="archive.db") | .browser_download_url') \
  -o archive.db
```

---

**STATUS:** 🟢 All archives stored permanently in GitHub Releases  
**COST:** FREE (within GitHub storage limits)  
**RETRIEVAL:** Always available, no expiration
