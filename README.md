# web-crawler

**ВНИМАНИЕ: ЭТОТ РЕПОЗИТОРИЙ — ИСКЛЮЧИТЕЛЬНО ДЛЯ ИИ.**  
**РЕЖИМ:** token-first (максимальная экономия токенов).  
**ЗАПРЕЩЕНО:** плодить сущности, разводить грязь документацией, создавать ненужные файлы/папки/конфиги.

## 🎯 Что здесь

- `.github/workflows/download-site.yml` — скачивает сайты через wget, создает artifacts
- `.gitignore` — стандартный Git-конфиг
- `README.md` — этот файл

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
4. ✅ Скачивает page requisites: CSS/JS/images (`-p`)
5. ✅ Добавляет расширения HTML (`--adjust-extension`)
6. ✅ Применяет random wait для этичного краулинга (`--random-wait`)
7. ✅ Проверяет архив (HTML count, minimum size 10KB)
8. ☁️ Загружает как artifact (30 дней retention)
9. 📄 Загружает wget.log как отдельный artifact (7 дней)
10. 📊 Создает job summary в Actions UI
11. 🔔 Отправляет callback в N8N с 3 retry попытками

**Concurrency:**
```yaml
group: download-{url}-{depth}
cancel-in-progress: true  # Отменяет дубли
```

**Timeouts:**
- Job: 60 минут
- Download step: 45 минут
- N8N callback: 10 секунд per attempt

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
  --page-requisites \
  --convert-links \
  --adjust-extension \
  --no-parent \
  --directory-prefix="$OUTPUT_DIR" \
  --timeout=30 \
  --tries=3 \
  --wait=2 \
  --random-wait \
  --user-agent="Mozilla/5.0 (compatible; ArchiveBot/1.0; +https://github.com/KomarovAI/web-crawler)" \
  --reject-regex='\?.*' \
  "$URL"
```

**Почему эти флаги:**
- `--recursive` — скачивает всю структуру сайта
- `--level=N` — ограничивает глубину краулинга
- `--page-requisites` — скачивает CSS/JS/images для каждой страницы (offline-ready)
- `--convert-links` — переписывает абсолютные ссылки → относительные
- `--adjust-extension` — добавляет `.html` если нет расширения
- `--no-parent` — не выходит выше стартовой директории
- `--timeout=30` — 30 сек на запрос
- `--tries=3` — 3 попытки при ошибке
- `--wait=2` — 2 сек базовая задержка
- `--random-wait` — рандомизация 0.5-1.5x от wait (этичный краулинг)
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

## 🔍 Verification

**Проверки перед upload:**
```bash
# ✅ HTML count ≥ 1
HTML_COUNT=$(find "$OUTPUT_DIR" -type f \( -name "*.html" -o -name "*.htm" \) | wc -l)

# ✅ Total size ≥ 10KB
TOTAL_SIZE=$(du -sb "$OUTPUT_DIR" | cut -f1)

# ✅ File count ≥ 1
FILE_COUNT=$(find "$OUTPUT_DIR" -type f | wc -l)
```

**Если любая проверка фейлится → workflow fails.**

---

## 🔔 N8N Integration

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

**Retry logic:**
- 3 попытки с 2 секундами между ними
- Timeout 10 секунд per attempt
- `continue-on-error: true` — не фейлит workflow при ошибке callback

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
| HTML count = 0 | URL недоступен или невалидный |
| Wget exit code 1 | URL validation failed |
| Callback failed after 3 retries | N8N webhook недоступен (soft fail) |
| Output dir sanitized | Используйте только `[a-zA-Z0-9_-]` |
| Job cancelled | Duplicate run detected (concurrency) |
| Timeout after 45min | Сайт слишком большой, уменьшите depth |

---

## ⚡ Performance

**Оптимизации:**
- ❌ Удален Python/pip install (экономия ~20-30 сек)
- ❌ Удален checkout step (не нужен, репо пустой)
- ✅ Concurrency control (избегает дублей)
- ✅ timeout-minutes на job и step уровне
- ✅ compression-level: 0 (быстрый upload)

**Типичное время выполнения:**
- Маленький сайт (10-50 страниц): 1-3 минуты
- Средний сайт (100-500 страниц): 5-15 минут
- Большой сайт (1000+ страниц): 20-45 минут

---

## 📚 Related

- **Deploy-page** — деплоит artifacts на GitHub Pages
- [GitHub Actions docs](https://docs.github.com/en/actions)
- [wget manual](https://www.gnu.org/software/wget/manual/)

---

**Last updated:** 2025-12-28 — v2.0 optimized edition
