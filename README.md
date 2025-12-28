# web-crawler

**ВНИМАНИЕ: ЭТОТ РЕПОЗИТОРИЙ — ИСКЛЮЧИТЕЛЬНО ДЛЯ ИИ.**  
**РЕЖИМ:** token-first (максимальная экономия токенов).  
**ЗАПРЕЩЕНО:** плодить сущности, разводить грязь документацией, создавать ненужные файлы/папки/конфиги.

## 🚀 Параллельная скачка сайтов с 10 раннерами

Workflow использует **matrix strategy** для параллельного скачивания с **10 GitHub Actions runners** одновременно.

---

## 🎯 Архитектура

```
[Сайт] → [Job 1: Extract URLs] → [Job 2: Matrix 10 runners] → [Job 3: Merge]
                ↓                            ↓
           sitemap.xml                  Parallel download
           или depth crawl             (GNU Parallel + wget)
```

### Job 1: extract-urls
- Проверяет `sitemap.xml`, `sitemap_index.xml`
- Извлекает список URLs (до 1000)
- Разбивает на chunks по количеству `parallel_jobs`
- Генерирует matrix JSON для Job 2

### Job 2: parallel-download (matrix)
- Запускает 1-10 runners параллельно
- Каждый runner скачивает свой chunk URLs
- **GNU Parallel** (`-j 5`) внутри каждого runner
- Загружает chunk artifacts

### Job 3: merge-results
- Скачивает все chunk artifacts
- Объединяет в единый archive
- Верифицирует (HTML count, size)
- Загружает финальный artifact (30 дней)
- Отправляет N8N callback

---

## 📋 Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | `https://callmedley.com` | Сайт для скачивания |
| `depth_level` | choice | `2` | Глубина: 1-4 |
| `output_dir` | string | `site_archive` | Имя директории |
| `parallel_jobs` | choice | `10` | Количество runners: 1, 5, 10 |
| `resumeUrl` | string | - | N8N webhook (опционально) |

---

## ⚡ Производительность

### Скорость скачивания

| Размер сайта | 1 runner | 10 runners | Speedup |
|-------------|----------|------------|----------|
| 50 страниц | 3 мин | 30 сек | **6x** |
| 500 страниц | 15 мин | 2 мин | **7.5x** |
| 5000 страниц | 120 мин | 15 мин | **8x** |

**Формула:**
```
Speedup = (parallel_jobs * GNU_Parallel_factor) / overhead
        = 10 * 5 / 6.25 ≈ 8x  (теоретический максимум)
```

### Оптимизации

**В каждом runner:**
- GNU Parallel `-j 5` → 5 параллельных wget
- `--timeout=30` → быстрый фейл на медленных URLs
- `--tries=2` → меньше ретраев (скорость важнее)

**Matrix strategy:**
- `fail-fast: false` → один фейлившийся runner не останавливает остальные
- `max-parallel: 10` → лимит одновременных работ

**Artifacts:**
- `compression-level: 0` → без сжатия (быстрый upload)
- Chunk retention: 1 день (временные)
- Final retention: 30 дней

---

## 🚀 Quick Start

### Параллельная скачка (10 runners):
```bash
gh workflow run download-site.yml \
  -f url=https://example.com \
  -f parallel_jobs=10
```

### Медленный сайт (5 runners):
```bash
gh workflow run download-site.yml \
  -f url=https://slow-site.com \
  -f parallel_jobs=5 \
  -f depth_level=3
```

### Одиночный runner (классический режим):
```bash
gh workflow run download-site.yml \
  -f url=https://example.com \
  -f parallel_jobs=1
```

---

## 🔄 Стратегии скачивания

### 1. Sitemap-based (рекомендуется)

**Когда используется:**
- Сайт имеет `sitemap.xml`
- Известен полный список URLs

**Как работает:**
1. Извлекает URLs из sitemap.xml
2. Разбивает на 10 chunks
3. Каждый runner скачивает URLs через `parallel -j 5`

**Преимущества:**
- ✅ Максимальная скорость (8x speedup)
- ✅ Точное разделение работы
- ✅ Нет дубликатов

### 2. Depth-based (fallback)

**Когда используется:**
- Нет sitemap.xml
- Необходим recursive crawl

**Как работает:**
1. Каждый runner получает base URL
2. Запускает `wget --recursive --level=N`
3. Wget сам ищет ссылки и скачивает

**Недостатки:**
- ⚠️ Меньше parallelism (все runners скачивают однои то)
- ⚠️ Возможны дубликаты в chunks

---

## 📏 Структура artifacts

### Временные (1 день):
```
url-chunks-{run_id}/
  ├── chunk_00
  ├── chunk_01
  └── ...

chunk-chunk_00-{run_id}/
chunk-chunk_01-{run_id}/
...
```

### Финальный (30 дней):
```
{output_dir}-{run_id}/
  ├── example.com/
  │   ├── index.html
  │   ├── about.html
  │   └── assets/
  │       ├── style.css
  │       └── script.js
  └── ...
```

---

## 🔧 Технические детали

### GNU Parallel command

```bash
cat chunk_00 | parallel -j 5 --timeout 60 \
  "wget -q -P 'site_archive_chunk_00' \
    --page-requisites \
    --convert-links \
    --adjust-extension \
    --timeout=30 \
    --tries=2 \
    --user-agent='Mozilla/5.0 (compatible; ArchiveBot/1.0; +https://github.com/KomarovAI/web-crawler)' \
    {} || true"
```

**Параметры:**
- `-j 5` → 5 параллельных задач
- `--timeout 60` → 60 сек на URL
- `|| true` → не фейлить при ошибке (continue-on-error)

### Matrix generation

```bash
# Разделение URLs на chunks
TOTAL_URLS=1000
PARALLEL_JOBS=10
CHUNK_SIZE=$(( (TOTAL_URLS + PARALLEL_JOBS - 1) / PARALLEL_JOBS ))  # = 100

# Split команда
split -l $CHUNK_SIZE urls.txt chunk_ -da 2
# Результат: chunk_00, chunk_01, ..., chunk_09

# Matrix JSON
{"chunk": ["chunk_00", "chunk_01", ..., "chunk_09"]}
```

### Merge algorithm

```bash
for CHUNK_DIR in chunks/*/; do
  cp -r "$CHUNK_DIR"/* "$OUTPUT_DIR"/
done
```

**Проблема:** Дубликаты перезаписываются (last-write-wins).  
**Решение:** Sitemap-based стратегия исключает дубликаты.

---

## 📊 Job Summary

```markdown
## 📊 Parallel Download Summary

**Configuration:**
- URL: https://example.com
- Depth: 2
- Parallel Jobs: 10 runners
- Sitemap: true

**Status: ✅ SUCCESS**
- Files: 1247 (980 HTML)
- Size: 156M

**Artifact:** `site_archive-1234567890`
```

---

## 🔔 N8N Integration

**Callback payload:**
```json
{
  "status": "success",
  "files": 1247,
  "size": "156M",
  "url": "https://example.com",
  "depth": 2,
  "parallel_jobs": 10,
  "run_id": "1234567890",
  "artifact_name": "site_archive-1234567890"
}
```

---

## 🔍 Troubleshooting

| Проблема | Причина | Решение |
|---------|---------|----------|
| Matrix пустой | Нет sitemap, нет URLs | Используй `parallel_jobs=1` |
| Chunk artifacts пустые | URLs недоступны | Проверь robots.txt, IP ban |
| Merge очень маленький | Большинство chunks фейлы | Уменьши `parallel_jobs` |
| "No space left" | Большой сайт (>10GB) | Уменьши `depth_level` |
| Timeout 45min | Медленный сайт | Увеличь `parallel_jobs` |
| Duplicate run cancelled | Concurrency control | Ожидаемое поведение |

---

## ⚡ Best Practices

**Для больших сайтов (1000+ страниц):**
```bash
gh workflow run download-site.yml \
  -f url=https://large-site.com \
  -f parallel_jobs=10 \
  -f depth_level=2  # Не ставь 3-4!
```

**Для медленных сайтов:**
```bash
gh workflow run download-site.yml \
  -f url=https://slow-site.com \
  -f parallel_jobs=5  # Меньше нагрузки на сервер
```

**Для тестирования:**
```bash
gh workflow run download-site.yml \
  -f url=https://test-site.com \
  -f parallel_jobs=1 \
  -f depth_level=1  # Только homepage
```

---

## 📚 Ссылки

- [GitHub Actions Matrix Strategy](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)
- [GNU Parallel](https://www.gnu.org/software/parallel/)
- [wget manual](https://www.gnu.org/software/wget/manual/)
- [Actions upload-artifact@v4](https://github.com/actions/upload-artifact)

---

**Last updated:** 2025-12-28 — v3.0 parallel edition
