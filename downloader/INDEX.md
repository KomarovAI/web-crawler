# 📄 DOWNLOADER MODULE - COMPLETE INDEX

## 🚀 START HERE

### 🙄 In a Hurry?
**[QUICKSTART.md](QUICKSTART.md)** - 30 seconds, pick your method, go!

### 📖 Want Full Details?
**[README.md](README.md)** - Complete guide with examples and troubleshooting

### 📂 Need Integration Info?
**[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** - All solutions, all methods explained

### 🔍 Want Implementation Details?
**This file** - Navigation and cross-references

---

## 💿 REFERENCE

### Executables
- **[cli.sh](cli.sh)** - Bash CLI script (chmod +x first)
- **[site_downloader.py](site_downloader.py)** - Python module
- **[Dockerfile.downloader](Dockerfile.downloader)** - Docker container

### Configuration
- **[requirements-downloader.txt](requirements-downloader.txt)** - Python dependencies

### Automation
- **[../.github/workflows/download-site.yml](../.github/workflows/download-site.yml)** - GitHub Actions

---

## 💎 6 WAYS TO USE

| # | Method | Command | Time | Install |
|---|--------|---------|------|----------|
| 1 | **CLI** | `./cli.sh download URL METHOD` | 30s | ✓ Ready |
| 2 | **Python** | `python3 site_downloader.py URL -m METHOD` | 30s | pip |
| 3 | **Docker** | `docker run ... download URL METHOD` | 2m | docker |
| 4 | **HTTrack** | `httrack URL -O . -k` | 30s | brew |
| 5 | **WGET** | `wget -m -p -k URL` | 30s | Built-in |
| 6 | **GitHub** | Click Actions → workflow | 2m | ✓ Ready |

### See detailed comparison in [QUICKSTART.md](QUICKSTART.md#-какой-выбрать)

---

## 💈 3 DOWNLOAD ENGINES

### HTTrack ⭐ (Recommended)
- **Best for:** Maximum control + reliability
- **Speed:** ⚡⚡⚡⚡ (4/5)
- **Control:** ⚡⚡⚡⚡⚡ (5/5)
- **Offline:** Yes, converts links
- **Size:** Full folder structure
- **Install:** `brew install httrack`
- **Learn more:** [README.md#httrack](README.md#httrack--recommended)

### WGET ⚡ (Built-in)
- **Best for:** Speed + simplicity
- **Speed:** ⚡⚡⚡⚡⚡ (5/5)
- **Control:** ⚡⚡⚡ (3/5)
- **Offline:** Yes, converts links
- **Size:** Full folder structure
- **Install:** Built-in or `brew install wget`
- **Learn more:** [README.md#wget--built-in](README.md#wget--built-in)

### Monolith 📦 (Single File)
- **Best for:** Archiving + sharing
- **Speed:** ⚡⚡⚡ (3/5)
- **Control:** ⚡ (1/5)
- **Offline:** Yes, fully embedded
- **Size:** Large single HTML
- **Install:** `brew install monolith`
- **Learn more:** [README.md#monolith--single-file](README.md#monolith--single-file)

---

## 📂 FILE STRUCTURE

```
downloader/
├─ INDEX.md                    ← YOU ARE HERE
├─ QUICKSTART.md               🚀 30-second start
├─ README.md                   📖 Full documentation
├─ INTEGRATION_SUMMARY.md      🐫 All details
├─ cli.sh                      ⚡ CLI script
├─ site_downloader.py         🚀 Python module
├─ Dockerfile.downloader      🐫 Docker build
└─ requirements-downloader.txt 📄 Dependencies

.github/workflows/
└─ download-site.yml          🔄 GitHub Actions

ROOT:
└─ README.md                  (🚀 with downloader section)
```

---

## 🙄 Quick Navigation

### "I want to download a website RIGHT NOW"
→ Go to [QUICKSTART.md](QUICKSTART.md)

### "I want to use the CLI"
→ Command: `./downloader/cli.sh download URL METHOD`
→ Details: [README.md - CLI](README.md#cli-examples)

### "I want to use Python"
→ Import: `from downloader.site_downloader import SiteDownloader`
→ Details: [README.md - Python Examples](README.md#python-examples)

### "I want to use Docker"
→ Build: `docker build -f downloader/Dockerfile.downloader -t downloader .`
→ Run: See [README.md - Docker Examples](README.md#docker-examples)

### "I want automation with GitHub"
→ Go to: Actions tab → Download Website workflow
→ Details: [.github/workflows/download-site.yml](../.github/workflows/download-site.yml)

### "I want to understand all options"
→ Go to [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)

### "I'm troubleshooting"
→ Go to [README.md - Troubleshooting](README.md#%EF%B8%8F-%D0%9D%D0%95-%D0%9E%D1%81%D1%82%D0%B0%D0%B1%D1%82%D0%B5%D1%81%D1%8C-%D0%9F%D0%B5%D1%80%D0%B5%D0%B4-%D0%9F%D1%80%D0%BE%D0%B1%D0%BB%D0%B5%D0%BC%D0%B0%D0%BC%D0%B8)

---

## 📊 QUICK COMMANDS

### Copy-Paste Ready

```bash
# HTTrack (recommended)
httrack https://callmedley.com -O ./site -k -%e -c16 --max-rate=0

# WGET
wget -m -p -k --domains callmedley.com --no-parent https://callmedley.com/

# Monolith
monolith https://callmedley.com/ -o site.html

# CLI script
chmod +x downloader/cli.sh
./downloader/cli.sh download https://callmedley.com httrack

# Python
python3 downloader/site_downloader.py https://callmedley.com -m all

# Docker
docker build -f downloader/Dockerfile.downloader -t downloader .
docker run -v $(pwd)/downloads:/app/downloads downloader \
  download https://callmedley.com httrack
```

---

## 🔍 FEATURE MATRIX

| Feature | HTTrack | WGET | Monolith | CLI | Python | Docker | GitHub |
|---------|---------|------|----------|-----|--------|--------|--------|
| Speed | ⚡⚡⚡⚡ | ⚡⚡⚡⚡⚡ | ⚡⚡⚡ | - | - | - | - |
| Control | ⚡⚡⚡⚡⚡ | ⚡⚡⚡ | ⚡ | - | - | - | - |
| Offline | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Install | `brew` | Built-in | `brew` | Ready | pip | docker | Ready |
| Single file | - | - | ✅ | - | - | - | - |
| Full structure | ✅ | ✅ | - | ✅ | ✅ | ✅ | ✅ |
| Automation | - | - | - | ✅ | ✅ | ✅ | ✅ |
| Programmable | - | - | - | - | ✅ | ✅ | - |

---

## 📁 File Sizes

### Code
- cli.sh: 6.2 KB
- site_downloader.py: 9.0 KB
- Dockerfile.downloader: 2.0 KB
- Total: ~17 KB

### Results
- Typical website: 10-200 MB (depends on size)
- Archive (.tar.gz): 5-100 MB
- Monolith (single file): 20-200 MB

---

## 🚀 Integration Points

### With Web Crawler (main repo)
- Use both: crawler for archival, downloader for local copies
- Chain workflows: crawl first, then download
- Complementary: crawler gets data, downloader gets files

### With Your Code
```python
# Import and use in your project
from downloader.site_downloader import SiteDownloader
downloader = SiteDownloader()
result = downloader.download(url, method='httrack')
```

### With CI/CD
- Use GitHub Actions workflow
- Or trigger from your own CI/CD
- Or run on schedule

---

## 🔓 Keyboard Shortcuts

### Navigation
- Quick start: [QUICKSTART.md](QUICKSTART.md)
- Full docs: [README.md](README.md)
- Integration: [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)
- This file: [INDEX.md](INDEX.md)

### Scripts
- CLI: [cli.sh](cli.sh)
- Python: [site_downloader.py](site_downloader.py)
- Docker: [Dockerfile.downloader](Dockerfile.downloader)
- GitHub: [download-site.yml](../.github/workflows/download-site.yml)

---

## 🎆 Tips & Tricks

### Maximum Speed
```bash
wget -m -p -k --wait=0 -P ./site https://example.com/
```

### Maximum Reliability
```bash
httrack https://example.com -O ./site -k --continue
```

### Minimum Size
```bash
monolith https://example.com/ -o archive.html
```

### Scheduled Downloads
```bash
# crontab
0 2 * * * /path/to/downloader/cli.sh download https://example.com httrack
```

### Batch Downloads
```bash
# Create urls.txt with one URL per line
while read url; do
  ./downloader/cli.sh download "$url" httrack
done < urls.txt
```

---

## ✅ Verification

### Check Installation
```bash
which wget
which httrack
which monolith
```

### Test Download
```bash
./downloader/cli.sh download https://example.com httrack
```

### Verify Output
```bash
ls -la downloads/
du -sh downloads/*
open downloads/*/index.html
```

---

## 📚 Resources

### Official Docs
- HTTrack: https://www.httrack.com/
- WGET: https://www.gnu.org/software/wget/
- Monolith: https://github.com/Y2Z/monolith

### This Repo
- Main README: [../../README.md](../../README.md)
- Web Crawler: [../../smart_archiver_v2.py](../../smart_archiver_v2.py)
- GitHub Actions: [../../.github/workflows/](../../.github/workflows/)

---

## 🌟 Next Steps

1. Pick your method from [QUICKSTART.md](QUICKSTART.md)
2. Read the examples
3. Run the command
4. Check the results
5. Done! 🎆

---

**Status:** ✅ Complete | **Quality:** Production-ready | **Methods:** 6 | **Engines:** 3

**Ready?** Start with [QUICKSTART.md](QUICKSTART.md)!
