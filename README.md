# web-crawler

**ВНИМАНИЕ: ЭТОТ РЕПОЗИТОРИЙ — ИСКЛЮЧИТЕЛЬНО ДЛЯ ИИ.**  
**РЕЖИМ:** token-first (максимальная экономия токенов).  
**ЗАПРЕЩЕНО:** плодить сущности, разводить грязь документацией, создавать ненужные файлы/папки/конфиги.

## 🎯 Что здесь

- `.github/workflows/download-site.yml` — скачивает сайты через wget, создает artifacts
- `.gitignore` — стандартный Git-конфиг
- `README.md` — этот файл
- `WORKFLOWS_GUIDE.md` — детальная документация workflow

---

## 📋 download-site.yml

**Trigger:** `workflow_dispatch` (ручной запуск)

**Inputs:**
- `url` (опционально, default: `https://callmedley.com`) — URL сайта для скачивания
- `depth_level` (опционально, default: `2`) — глубина краулинга:
  - `1` = только homepage
  - `2` = homepage + дочерние страницы (default)
  - `3` = homepage + 2 уровня вглубь
  - `4` = очень глубокий краулинг
- `output_dir` (опционально, default: `site_archive`) — имя директории для выхода (alphanumeric, dash, underscore)
- `resumeUrl` (опционально) — N8N webhook URL для callback

**Что делает:**

1. ✅ Валидирует inputs (URL format, depth range, sanitized output_dir)
2. 🌐 Скачивает сайт через `wget --recursive` с заданной глубиной
3. ✅ Конвертирует ссылки в относительные (`--convert-links`)
4. ✅ Добавляет расширения HTML (`--adjust-extension`)
5. ✅ Применяет timeout/retry (30s timeout, 3 tries)
6. 📦 Верифицирует архив (file count, size)
7. ☁️ Загружает как artifact (30 дней retention)
8. 📊 Создает job summary в Actions UI
9. 🔔 Отправляет callback в N8N (если `resumeUrl` указан)

**Outputs (artifact):**
- Имя: `{output_dir}-{run_id}`
- Путь: весь контент из `{output_dir}/`
- Compression: level 0 (без сжатия для скорости)
- Retention: 30 дней

**Outputs (N8N callback):**
```json
{
  "status": "success",
  "files": 42,
  "size": "15M",
  "url": "https://callmedley.com",
  "depth": 2,
  "time": 120,
  "run_id": "1234567890",
  "artifact_name": "site_archive-1234567890"
}
```

---

## 🚀 Quick Start

### Basic download (default depth=2):
```bash
gh workflow run download-site.yml \
  -f url=https://example.com
```

### Deep crawl (depth=4):
```bash
gh workflow run download-site.yml \
  -f url=https://example.com \
  -f depth_level=4 \
  -f output_dir=example_deep
```

### With N8N callback:
```bash
gh workflow run download-site.yml \
  -f url=https://callmedley.com \
  -f resumeUrl=https://your-n8n.com/webhook/abc123
```

---

## 🔧 Wget Flags

```bash
wget --recursive \
  --level="$DEPTH" \
  --convert-links \
  --adjust-extension \
  --no-parent \
  --directory-prefix="$OUTPUT_DIR" \
  --timeout=30 \
  --tries=3 \
  --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  --reject-regex='\?.*' \
  "$URL"
```

**Почему эти флаги:**
- `--recursive` — скачивает всю структуру сайта
- `--level=N` — ограничивает глубину краулинга
- `--convert-links` — переписывает абсолютные ссылки → относительные
- `--adjust-extension` — добавляет `.html` если нет расширения
- `--no-parent` — не выходит выше стартовой директории
- `--timeout=30` — 30 сек на запрос
- `--tries=3` — 3 попытки при ошибке
- `--reject-regex='\?.*'` — игнорирует query strings (избегает дублей)

---

## 📊 Exit Codes

| Code | Meaning | Workflow Result |
|------|---------|----------------|
| 0 | Success | ✅ SUCCESS |
| 8 | Server error (404, 500, etc.) | ✅ SUCCESS (partial download OK) |
| Other | Fatal error | ❌ FAILED |

**Почему exit code 8 считается успехом:**  
Сайты часто имеют несколько сломанных ссылок (404). Если основной контент скачан, это успех.

---

## 🔐 N8N Integration

**Workflow → N8N callback payload:**
```json
{
  "status": "success" | "failed",
  "files": 42,
  "size": "15M",
  "url": "https://callmedley.com",
  "depth": 2,
  "time": 120,
  "run_id": "1234567890",
  "artifact_name": "site_archive-1234567890"
}
```

**Использование в N8N:**
1. Создайте Webhook node
2. Скопируйте Production URL
3. Передайте в workflow как `resumeUrl`
4. Парсите `artifact_name` для download через GitHub API

---

## 🔧 Common Issues

| Issue | Fix |
|-------|-----|
| Artifact empty | Сайт требует JS или блокирует wget |
| File count = 0 | URL недоступен или неверный |
| Wget exit code 1 | URL validation failed |
| Callback failed | N8N webhook недоступен (soft fail) |
| Output dir sanitized | Используйте только `[a-zA-Z0-9_-]` |

---

## 📚 Related

- **Deploy-page** — деплоит artifacts на GitHub Pages
- [GitHub Actions docs](https://docs.github.com/en/actions)
- [wget manual](https://www.gnu.org/software/wget/manual/)

---

**Last updated:** 2025-12-28 — v1.0 minimal token-first edition
