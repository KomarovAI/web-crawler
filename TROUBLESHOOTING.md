# 🔧 TROUBLESHOOTING GUIDE

## 🔍 ISSUES FOUND & FIXED

### Issue #1: ❌ `crawler.py` Not Found
**Error in logs:**
```
ModuleNotFoundError: No module named 'crawler'
```

**Cause:** Workflow was calling `python crawler.py` but file doesn't exist

**Fix:** Changed to `python3 smart_archiver_v2.py`

---

### Issue #2: ❌ httrack Silent Failure
**Error in logs:**
```
[ERROR] httrack failed: * 
```

**Cause:** httrack called without proper arguments or timed out

**Solution:**
```python
# Now using async subprocess with proper error handling:
async def download_with_httrack(self, url):
    cmd = [
        'httrack',
        url,
        '-O', str(output_dir),
        '-%e',           # Save structure
        '-k',            # Convert links
        '--max-rate=0',  # No speed limit
        '-c16'           # 16 threads
    ]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logger.error(f"httrack failed: {stderr.decode()}")
        return {'success': False, 'error': stderr.decode()}
```

---

### Issue #3: ⏱️ Timeout Issues
**Error:**
```
TimeoutError: Operation timed out
```

**Fix in workflow:**
```yaml
# Before: timeout-minutes: 60
# After:
timeout-minutes: 120  # Increased for full-site downloads
```

**Fix in code:**
```python
# Before: timeout=60
# After:
timeout = aiohttp.ClientTimeout(total=120)
```

---

## 🔍 COMMON ERRORS & SOLUTIONS

### Error: Database locked
**Symptom:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```python
# Already implemented in code:
self.conn.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging
self.conn.execute('PRAGMA synchronous=OFF')    # Faster writes
```

---

### Error: Out of memory
**Symptom:**
```
MemoryError: Unable to allocate X.XX GiB
```

**Solution:** Reduce max_pages or max_depth:
```python
archiver = WARCCompliantArchiver(
    start_url='https://example.com',
    max_depth=2,        # Reduce from 5
    max_pages=100       # Reduce from 500
)
```

---

### Error: Connection refused
**Symptom:**
```
aiohttp.ClientConnectorError: Cannot connect to host
```

**Solution:** Website may be down or blocking. Check manually:
```bash
curl -I https://example.com
```

---

### Error: SSL certificate verification failed
**Symptom:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solution:** Already handled in code:
```python
async with session.get(url, ssl=True, allow_redirects=True) as response:
    # ssl=True enables certificate verification
```

For testing only (NOT production):
```python
import ssl
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

connector = aiohttp.TCPConnector(ssl=ssl_context)
```

---

## 🔍 WORKFLOW ISSUES

### Issue: Artifact not uploaded
**Error:**
```
##[warning]No files were found with the provided path: archive.db
```

**Cause:** Crawler failed silently, DB not created

**Solution:** Check crawler output in logs. Look for:
- Connection errors
- Module import errors
- Syntax errors

---

### Issue: pip cache not working
**Error:**
```
Cache not found for input keys: pip-...
```

**Solution:** First run doesn't have cache (normal). Subsequent runs will cache.

---

### Issue: httrack/wget not found
**Error:**
```
E: Unable to locate package httrack
```

**Solution:** Already handled in workflow. Run manually if needed:
```bash
sudo apt-get update
sudo apt-get install httrack wget
```

---

## 🔍 DEBUG TIPS

### 1. Run locally to test
```bash
# Install dependencies
pip install -r requirements.txt

# Install system tools
sudo apt-get install httrack wget lxml

# Run crawler
python3 smart_archiver_v2.py https://example.com 5
```

### 2. Check database
```bash
# Inspect archive.db
sqlite3 archive.db

# List all tables
.tables

# Check page count
SELECT COUNT(*) FROM pages;

# Check download stats
SELECT * FROM downloaded_files LIMIT 10;

# Check download metadata
SELECT * FROM download_metadata;
```

### 3. Increase logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Was: INFO
```

### 4. Test httrack separately
```bash
httrack https://example.com -O ./test_download -k -c16 --max-rate=0
```

### 5. Test wget separately
```bash
wget --mirror --page-requisites --convert-links \
  -P ./test_download \
  https://example.com
```

---

## 👢 PRODUCTION CHECKLIST

Before deploying to production:

- [ ] Test with small website (max_depth=2, max_pages=50)
- [ ] Verify database integrity with verification script
- [ ] Monitor GitHub Actions minutes usage
- [ ] Check artifact storage limits
- [ ] Test fallback: wget works if httrack fails
- [ ] Verify SSL certificates are valid
- [ ] Test with different domain types (.com, .org, etc)
- [ ] Monitor for rate limiting (use --wait in wget)

---

## 🔍 PERFORMANCE PROFILING

### Measure crawl speed
```bash
time python3 smart_archiver_v2.py https://example.com 5
```

### Check memory usage
```bash
# In another terminal:
watch -n 1 'ps aux | grep smart_archiver'
```

### Monitor database size
```bash
watch -n 1 'ls -lh archive.db'
```

### Check network usage
```bash
iftop -i eth0
```

---

## 🔍 GETTING HELP

### Check GitHub Actions logs:
1. Go to your repository
2. Click "Actions" tab
3. Click workflow run
4. Scroll to failed step
5. Click "Run [step name]" to expand

### Common log locations:
- `httrack download` section: Shows httrack output
- `Run crawler + full-site download` section: Shows Python errors
- `COMPREHENSIVE VERIFICATION` section: Shows database issues

### Emergency debug mode:
```yaml
- name: Debug info
  if: always()
  run: |
    echo "Python version:"
    python3 --version
    
    echo "\nInstalled packages:"
    pip list
    
    echo "\nHTTrack installed:"
    which httrack
    httrack --version
    
    echo "\nDatabase status:"
    ls -lh *.db || echo "No database files found"
    
    echo "\nDisk space:"
    df -h
```

---

**Status:** 🟢 **All known issues fixed**
