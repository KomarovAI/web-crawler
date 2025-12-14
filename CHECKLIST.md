# ✅ Setup Checklist

## Before First Run

- [ ] Clone repository
  ```bash
  git clone https://github.com/KomarovAI/web-crawler.git
  cd web-crawler
  ```

- [ ] Create virtual environment
  ```bash
  python -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  ```

- [ ] Install dependencies
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Setup environment file
  ```bash
  cp .env.example .env
  # Edit .env and set START_URL
  ```

- [ ] Test crawler
  ```bash
  python crawler.py
  ```

## Configuration

- [ ] `.env` file created
  - [ ] `START_URL` set to your domain
  - [ ] `MAX_PAGES` configured (default 50)
  - [ ] `TIMEOUT` configured (default 10)

- [ ] `.gitignore` in place (already added)
  - [ ] .env is excluded
  - [ ] __pycache__ is excluded
  - [ ] .venv is excluded

## Security Checklist

- [ ] `.env` file is in `.gitignore`
  ```bash
  cat .gitignore | grep .env
  ```

- [ ] No credentials in code
  ```bash
  grep -r "password\|api_key\|secret" *.py
  ```

- [ ] GitHub repo is PRIVATE
  - [ ] Go to Settings → Privacy
  - [ ] Confirm "Private" is selected

- [ ] No sensitive data in commits
  ```bash
  git log --all --full-history -- .env
  ```

## Docker Setup (Optional)

- [ ] Docker installed
  ```bash
  docker --version
  ```

- [ ] Docker Compose installed
  ```bash
  docker-compose --version
  ```

- [ ] Build image
  ```bash
  docker build -t web-crawler .
  ```

- [ ] Test with Docker
  ```bash
  docker-compose up
  ```

## AI Integration Setup

- [ ] Read `AI_INTEGRATION.md`
- [ ] Review `AI_CONTEXT.txt`
- [ ] Check `PROMPTS.md` for examples
- [ ] Copy minimal context for first AI request

## Testing

- [ ] Manual test with small max_pages
  ```bash
  # In .env, set MAX_PAGES=5
  python crawler.py
  # Should complete in <30 seconds
  ```

- [ ] Check output format
  ```
  [1/5] https://...
  [2/5] https://...
  ✅ Crawled 5 pages
  ```

- [ ] Install test dependencies
  ```bash
  pip install pytest pytest-asyncio
  ```

- [ ] Run tests (if created)
  ```bash
  pytest tests/ -v
  ```

## Code Quality

- [ ] Type hints check
  ```bash
  pip install mypy
  mypy crawler.py
  ```

- [ ] Linting
  ```bash
  pip install flake8
  flake8 crawler.py
  ```

- [ ] Format check
  ```bash
  pip install black
  black --check .
  ```

## Deployment Preparation

- [ ] All dependencies in `requirements.txt`
  ```bash
  pip freeze > requirements.txt
  ```

- [ ] README.md complete
  - [ ] Setup instructions
  - [ ] Configuration documented
  - [ ] Examples provided

- [ ] GitHub Actions configured
  - [ ] CI/CD workflow in `.github/workflows/`
  - [ ] Tests pass in CI

- [ ] `.env.example` complete
  - [ ] All required variables listed
  - [ ] Helpful comments added

## Performance

- [ ] Concurrent requests optimized
  ```python
  # Check TCPConnector limit in crawler.py
  # Currently set to 5
  ```

- [ ] Rate limiting configured
  ```python
  # Check asyncio.sleep() duration
  # Currently set to 0.1 seconds
  ```

- [ ] Memory usage acceptable
  - [ ] Tested with MAX_PAGES=1000
  - [ ] No memory leaks detected

## Documentation

- [ ] README.md written
- [ ] QUICKSTART.md available
- [ ] PROJECT_SUMMARY.md readable
- [ ] AI_INTEGRATION.md complete
- [ ] PROMPTS.md has examples
- [ ] Inline code comments added
- [ ] Docstrings for functions

## Version Control

- [ ] Initial commit made
  ```bash
  git status  # should be clean
  git log --oneline | head
  ```

- [ ] Main branch protected (on GitHub)
  - [ ] Settings → Branches
  - [ ] Add rule for `main`
  - [ ] Require pull request reviews

- [ ] License file included
  - [ ] LICENSE file present
  - [ ] MIT License used

## Monitoring

- [ ] Logging configured
  ```python
  # Check LOG_LEVEL in .env
  ```

- [ ] Error handling in place
  - [ ] fetch() handles all errors
  - [ ] parse() is safe
  - [ ] No unhandled exceptions

- [ ] Status reporting
  ```python
  # Currently prints [n/max] for each page
  ```

## Collaboration

- [ ] Invited collaborators (if needed)
  - [ ] Settings → Collaborators
  - [ ] Added team members

- [ ] Created Issues (for tasks)
  - [ ] Feature requests
  - [ ] Bug reports
  - [ ] Improvements

- [ ] Setup branch protection (if team)
  - [ ] Require code review
  - [ ] Require status checks
  - [ ] Dismiss stale PR approvals

## Final Checks

- [ ] Clone in new directory and test
  ```bash
  cd /tmp
  git clone [your-repo]
  cd web-crawler
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  cp .env.example .env
  python crawler.py  # should work
  ```

- [ ] README has clear setup instructions
  - [ ] Works for Windows
  - [ ] Works for Mac
  - [ ] Works for Linux

- [ ] All sensitive data removed
  - [ ] No .env in commits
  - [ ] No API keys visible
  - [ ] No credentials in code

## 🌟 Ready to Deploy!

- [ ] All checks passed
- [ ] Documentation complete
- [ ] Security verified
- [ ] Code tested
- [ ] Repository private

**Status**: ✅ Ready for production

---

**Last checked**: 2025-12-14
**By**: AI Integration Setup
