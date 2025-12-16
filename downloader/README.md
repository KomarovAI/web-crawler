# 🚀 ULTIMATE WEBSITE DOWNLOADER

Фантастичная интеграция трёх данных ангинов для максимального контроля и скорости.

**🌟 FEATURES:**
- ⚡ Три совершенных мотора: **HTTrack**, **WGET**, **Monolith**
- 🐫 Docker ни каких зависимостей
- 💎 Простые CLI команды
- 🚀 Python модуль для програмного использования
- 🔄 GitHub Actions для автоматизации

---

## 🚀 QUICK START

### 1. … CLI (самый быстрый способ)

```bash
# Чистая копия HTTrack (recommended)
./downloader/cli.sh download https://callmedley.com httrack

# или WGET
./downloader/cli.sh download https://callmedley.com wget

# или всё три
./downloader/cli.sh download https://callmedley.com all
```

**Result:** Папка `downloads/` с полной копией сайта

---

### 2. 🚀 Python Module

```python
from downloader.site_downloader import SiteDownloader

# Просто
 downloader = SiteDownloader()
result = downloader.download('https://callmedley.com', method='httrack')

# Ор всё три
results = downloader.download_all('https://callmedley.com')
```

**Command line:**
```bash
python3 downloader/site_downloader.py https://callmedley.com -m httrack
python3 downloader/site_downloader.py callmedley.com -m all --dir ./archives
```

---

### 3. 🐫 Docker

```bash
# Build image
docker build -f downloader/Dockerfile.downloader -t web-downloader .

# Run download
docker run -v $(pwd)/downloads:/app/downloads web-downloader \
  download https://callmedley.com httrack

# One-liner (all methods)
docker run -v $(pwd)/downloads:/app/downloads web-downloader \
  download https://callmedley.com all
```

---

### 4. 🔄 GitHub Actions

1. Откройте repo на GitHub
2. Найдите **Actions** → **Download Website**
3. Нажмите **Run workflow**
4. Введите URL и метод
5. Получите artifacts

---

## 📚 ДЕТАЛЬНО

### HTTrack ⭐ (Recommended)

**Pros:**
- ✅ Максимальный контроль
- ✅ Перенаписывает ссылки
- ✅ Офлайн работа
- ✅ Надёжна

**Cons:**
- ❌ Нужна установка

**Install:**
```bash
# macOS
brew install httrack

# Linux
sudo apt-get install httrack

# Docker (included)
```

**Speed:** ⚡⚡⚡⚡ (4/5)
**Control:** ⚡⚡⚡⚡⚡ (5/5)

---

### WGET ⚡ (Built-in)

**Pros:**
- ✅ Встроен не все системы
- ✅ От супер-быстрый
- ✅ Простой

**Cons:**
- ❌ Меньше контролю

**Speed:** ⚡⚡⚡⚡⚡ (5/5)
**Control:** ⚡⚡⚡ (3/5)

---

### MONOLITH 📦 (Single File)

**Pros:**
- ✅ Один HTML файл
- ✅ Всё встроено
- ✅ Легко отправить

**Cons:**
- ❌ Большие файлы
- ❌ Сложнее эдитирование

**Install:**
```bash
# macOS
brew install monolith

# Rust
cargo install monolith --locked
```

**Speed:** ⚡⚡⚡ (3/5)
**Control:** ⚡ (1/5)

---

## 🚀 КОММАНДЫ

### CLI Examples

```bash
# HTTrack (super-recommended)
./downloader/cli.sh download https://callmedley.com httrack

# WGET
./downloader/cli.sh download https://callmedley.com wget

# Monolith
./downloader/cli.sh download https://callmedley.com monolith

# All three methods
./downloader/cli.sh download https://callmedley.com all

# Auto-add https://
./downloader/cli.sh download callmedley.com httrack
```

### Python Examples

```bash
# Default (httrack)
python3 downloader/site_downloader.py https://example.com

# Specific method
python3 downloader/site_downloader.py https://example.com -m wget

# Custom output directory
python3 downloader/site_downloader.py https://example.com -m all -d ./archives

# Verbose output
python3 downloader/site_downloader.py https://example.com -v
```

### Docker Examples

```bash
# Build
docker build -f downloader/Dockerfile.downloader -t downloader .

# HTTrack
docker run -v $(pwd)/downloads:/app/downloads downloader \
  download https://example.com httrack

# All methods
docker run -v $(pwd)/downloads:/app/downloads downloader \
  download https://example.com all

# Custom ports
docker run -v $(pwd)/downloads:/app/downloads downloader \
  download https://example.com:8080 httrack
```

---

## 📊 ФАЙЛОВАЯ СТРУКТУРА

```
downloader/
├─ cli.sh                    # Быстрая CLI
├─ site_downloader.py       # Python модуль
├─ Dockerfile.downloader    # Docker container
├─ requirements-downloader.txt
├─ README.md                 # Этот файл
└─ examples/                 # Примеры

.github/workflows/
└─ download-site.yml        # GitHub Actions

downloads/
└─ (results come here)
```

---

## ✅ Тестирование

```bash
# Test all methods
./downloader/cli.sh download https://example.com all

# Check downloads
ls -la downloads/

# Size check
du -sh downloads/*

# Open result
open downloads/httrack_*/example.com/index.html
```

---

## 💺 НЕ Остабтесь Перед Проблемами

### "httrack: command not found"
```bash
brew install httrack  # macOS
sudo apt-get install httrack  # Linux
```

### "wget: command not found"
Wget встроен, но может не отсутствовать:
```bash
brew install wget  # macOS
sudo apt-get install wget  # Linux
```

### "monolith: command not found"
```bash
brew install monolith  # macOS
cargo install monolith --locked  # Rust
```

### Docker build fails
```bash
# Try again with no cache
docker build --no-cache -f downloader/Dockerfile.downloader -t downloader .
```

---

## 🔍 Что дальше?

- ⭐ Star this repo if you like it!
- 🔗 See main [README.md](../README.md) for crawler functionality
- 📂 Check out [examples/](examples/) for more use cases
- 📧 Issues? Open a GitHub issue

---

**Made with ❤️ by DevOps Engineers**
