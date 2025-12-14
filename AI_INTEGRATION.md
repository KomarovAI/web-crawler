# AI Integration Guide 🤖

Заполнение контекста для нейронок с минимумом токенов.

## Quick Context (копировать в контекст нейронки)

```
## WEB CRAWLER PROJECT
- Language: Python 3.11
- Async crawler с aiohttp, BeautifulSoup
- Max pages: configurable, default 50
- Domain limitation: одноменный краулинг

## KEY FILES
1. crawler.py - основной класс Crawler(start_url, max_pages, timeout)
   - async fetch() - загрузка HTML
   - async parse() - извлечение ссылок
   - async run() - главный loop
2. config.py - переменные окружения
3. requirements.txt - 3 зависимости

## ARCHITECTURE
Crawler → queue-based BFS
  ├─ fetch(url) → HTML|None
  ├─ parse(html) → links[]
  └─ validate(url) → bool (domain, visited, max_pages)

## ENVIRONMENT
START_URL=https://example.com
MAX_PAGES=50
TIMEOUT=10
```

## Интеграция с AI

### Для Code Generation
Копируй этот контекст:
```
Проект: Web Crawler на Python
Рамки: <400 строк кода, 3 файла
Техстек: aiohttp, BeautifulSoup4, asyncio
Требования: минимум зависимостей, production-ready, типизация
```

### Для Analysis
```
Анализируй эти файлы:
- crawler.py (класс Crawler, методы fetch/parse/run)
- config.py (переменные)
- requirements.txt (зависимости)
Найди: баги, оптимизации, security issues
```

## Token Counter

**Текущие размеры:**
- crawler.py: ~140 строк (~420 токенов)
- config.py: ~18 строк (~40 токенов)
- requirements.txt: ~3 строки (~10 токенов)
- Docker: ~15 строк (~30 токенов)

**TOTAL: ~500 токенов** (самый компактный вариант)

## Optimization Tips

✅ Используй только нужные файлы (не груз весь репо)
✅ Передавай только дельту изменений
✅ Используй этот файл как reference вместо кода
✅ Для больших изменений - новая ветка

## Repository Structure

```
web-crawler/
├── crawler.py           (async crawler)
├── config.py            (config)
├── requirements.txt      (deps: 3 only)
├── docker-compose.yml    (optional)
├── Dockerfile            (optional)
├── .env.example          (config template)
├── .gitignore            (security)
├── LICENSE               (MIT)
├── README.md             (short)
├── AI_INTEGRATION.md     (this file)
└── .github/workflows/
    └── tests.yml         (CI/CD)
```
