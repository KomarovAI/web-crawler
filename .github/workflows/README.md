# GitHub Actions Workflows

## deploy-pages.yml

**Purpose:** Deploy archived websites to GitHub Pages (`gh-pages` branch)

### Trigger

```bash
gh workflow run deploy-pages.yml \
  --field source_run_id=20449810118 \
  --field artifact_name=site-archive-20449810118 \
  --field target_repo=KomarovAI/archived-sites \
  --field clean_warc=true \
  --field rewrite_links=true
```

### Required Secrets

- `EXTERNAL_REPO_PAT` - GitHub Personal Access Token (with `repo` scope for target repo)

### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source_run_id` | string | YES | - | Run ID from `download-site.yml` (numeric) |
| `artifact_name` | string | YES | - | Artifact name (e.g., `site-archive-20449810118`) |
| `target_repo` | string | YES | `KomarovAI/archived-sites` | Target repo for Pages deployment |
| `clean_warc` | boolean | NO | `true` | Remove WARC/WARC.gz files (GitHub 100MB limit) |
| `rewrite_links` | boolean | NO | `true` | Rewrite URLs to local paths |
| `resumeUrl` | string | NO | - | n8n webhook callback URL |

### Workflow Steps

1. **Validate inputs** - Check numeric run ID, repo format
2. **Download artifact** - Fetch site archive from source workflow
3. **Extract & verify** - Validate archive structure, count files
4. **Checkout target repo** - Clone target Pages repository
5. **Delete old gh-pages** - Clean previous deployment
6. **Initialize gh-pages** - Create fresh orphan branch (preserves `.git`)
7. **Copy archive** - Transfer site files to deployment directory
8. **Clean WARC files** - Remove large archive formats
9. **Rewrite URLs** - Convert absolute to relative links (Python)
10. **Commit & push** - Force push to `gh-pages` branch
11. **Create summary** - Post deployment status to run summary
12. **Notify n8n** - Send webhook callback with metrics

### Known Issues & Fixes

#### Issue: Git repository not found

**Symptom:** `fatal: not a git repository (or any of the parent directories): .git`

**Root Cause:** `.git` directory was being removed during orphan branch cleanup

**Fix:** Use selective file removal that preserves `.git`

```bash
# Instead of: rm -rf * .* (removes everything including .git)
find . -maxdepth 1 \
  -not -name '.git' \
  -not -name '.' \
  -not -name '..' \
  \( -type f -o -type d \) \
  -exec rm -rf {} + 2>/dev/null || true
```

### Testing Locally

```bash
bash scripts/test-orphan-branch.sh
```

This validates:
- ✅ Orphan branch creation
- ✅ Working directory cleanup
- ✅ `.git` directory preservation
- ✅ Initial commit creation

### Performance Metrics

| Metric | Value |
|--------|-------|
| Average runtime | 30-45 seconds |
| File copy speed | O(n) linear |
| URL rewrite speed | O(n) Python regex |
| Force push overhead | < 2 seconds |

### Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `Archive directory not found` | Artifact download failed | Verify source run ID exists |
| `target_repo format invalid` | Wrong format | Use `owner/repo` format |
| `source_run_id must be numeric` | Non-numeric input | Pass numeric run ID |
| `fatal: not a git repository` | `.git` was deleted | ✅ Fixed in v1.1.0 |

### References

- [Workflow file](.github/workflows/deploy-pages.yml)
- [Test script](../scripts/test-orphan-branch.sh)
- [Detailed fix documentation](../docs/DEPLOYMENT_FIX.md)
