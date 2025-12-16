# 🚀 QUICKSTART - 30 SECONDS TO DOWNLOAD ANY SITE

## 👆 Самые быстрые команды

### ⭐ СПОСОБ 1: HTTrack (РЕКОМЕНДУЕТСЯ)

```bash
# Install (first time only)
brew install httrack

# Download
httrack https://callmedley.com -O ./site -k -%e -c16 --max-rate=0
```

**Result:** Папка `site/` → Откройте `site/callmedley.com/index.html` ✅

---

### ⚡ СПОСОБ 2: WGET (Built-in)

```bash
wget -m -p -k --domains callmedley.com --no-parent \
  -P ./site https://callmedley.com/
```

**Result:** Папка `site/callmedley.com/` ✅

---

### 📦 СПОСОБ 3: MONOLITH (One file)

```bash
# Install
brew install monolith

# Download
monolith https://callmedley.com/ -o site.html
```

**Result:** `site.html` (один файл, откройте в браузере) ✅

---

### 🐫 СПОСОБ 4: Docker (No install)

```bash
# Build (first time only)
docker build -f downloader/Dockerfile.downloader -t downloader .

# Download
docker run -v $(pwd)/downloads:/app/downloads downloader \
  download https://callmedley.com httrack
```

**Result:** `downloads/` ✅

---

### 💎 СПОСОБ 5: CLI Script

```bash
# Make executable
chmod +x downloader/cli.sh

# Download
./downloader/cli.sh download https://callmedley.com httrack

# Or all three methods
./downloader/cli.sh download https://callmedley.com all
```

**Result:** `downloads/` ✅

---

### 🚀 СПОСОБ 6: Python

```bash
# Install dependencies
pip install -r downloader/requirements-downloader.txt

# Download
python3 downloader/site_downloader.py https://callmedley.com -m httrack

# Or with options
python3 downloader/site_downloader.py callmedley.com -m all -d ./archives -v
```

**Result:** `downloads/` ✅

---

## 🔧 Какой выбрать?

| Метод | Скорость | Контроль | Установка | Рекомендация |
|-------|---------|---------|-----------|-------------|
| **HTTrack** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | brew | 🙋 ЛУЧ |
| **WGET** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✓ Built-in | ⚡Ω БЫСТРО |
| **Monolith** | ⭐⭐⭐ | ⭐ | brew | 📦 1 ФАЙЛ |
| **Docker** | ⭐⭐⭐ | ⭐⭐⭐⭐ | docker | 🎯 НАДЁЖНО |
| **CLI** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✓ Ready | ✅ ПРОСТО |
| **Python** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | pip | 🚀 ГИБКО |

---

## 📊 РЕЗУЛЬТАТЫ

### HTTrack результат:
```
downloads/
└── httrack_20251216_191000/
    ├── callmedley.com/
    │   ├── index.html
    │   ├── assets/
    │   │   ├── css/
    │   │   ├── js/
    │   │   └── images/
    │   ├── favicon.ico
    │   └── ...
    └── hts-log.txt

✅ Откройте: downloads/httrack_.../callmedley.com/index.html
```

### WGET результат:
```
downloads/
└── wget_20251216_191000/
    ├── callmedley.com/
    │   ├── index.html
    │   └── assets/
    ├── callmedley.com.warc
    └── ...

✅ Откройте: downloads/wget_.../callmedley.com/index.html
```

### Monolith результат:
```
downloads/
└── monolith_callmedley_20251216_191000.html (50-200 MB)

✅ Откройте: downloads/monolith_*.html
```

---

## 🔓 СОВЕТЫ

### 1. Максимальная скорость
```bash
# HTTrack с 32 потоками (для быстрых интернета)
httrack https://example.com -O ./site -k -%e -c32 --max-rate=0
```

### 2. Ограничить размер
```bash
# Только HTML и CSS (без больших медиа)
httrack https://example.com -O ./site -k -%e -N100000 -*.mp4 -*.mov
```

### 3. Продолжить прерванную загрузку
```bash
# HTTrack автоматически продолжит
httrack https://example.com -O ./site -k -%e --continue
```

### 4. Проверить что загрузилось
```bash
# Размер
du -sh downloads/*

# Количество файлов
find downloads -type f | wc -l

# Список
ls -la downloads/*/
```

### 5. Создать архив
```bash
# TAR.GZ
tar -czf website_backup.tar.gz downloads/

# ZIP
zip -r website_backup.zip downloads/

# 7Z (максимальное сжатие)
7z a website_backup.7z downloads/
```

---

## ❌ ПРОБЛЕМЫ?

### "Command not found"
```bash
# Установите инструмент
brew install httrack
brew install monolith
brew install wget  # Обычно встроен, но может отсутствовать
```

### "Permission denied"
```bash
# Дайте прав на скрипт
chmod +x downloader/cli.sh
```

### "Docker build failed"
```bash
# Используйте --no-cache
docker build --no-cache -f downloader/Dockerfile.downloader -t downloader .
```

### "Timeout или ошибки сети"
```bash
# Увеличьте время ожидания и попробуйте снова
httrack https://example.com -O ./site -k -c8 --wait=2 --continue
```

---

## 🌟 ЛУЧШИЕ ПРАКТИКИ

✅ **DO:**
- Используйте HTTrack для лучшего контроля
- Проверьте robots.txt перед загрузкой
- Используйте --wait для соблюдения rate limiting
- Сохраняйте резервные копии

❌ **DON'T:**
- Не перегружайте серверы (используйте --wait)
- Не игнорируйте robots.txt
- Не скачивайте весь интернет
- Не распространяйте пиратский контент

---

## 📕 ДОПОЛНИТЕЛЬНО

- Полная документация: [README.md](README.md)
- GitHub repo: [KomarovAI/web-crawler](https://github.com/KomarovAI/web-crawler)
- HTTrack docs: [www.httrack.com](https://www.httrack.com)
- WGET docs: [gnu.org/wget](https://www.gnu.org/software/wget/)

---

**Ready? Pick your method above and go! 🚀**
