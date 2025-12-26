# GitHub Actions Workflows Documentation

## 📋 Overview

This repository uses optimized GitHub Actions workflows following modern best practices for CI/CD and deployment.

---

## 🚀 Workflows

### 1. **Deploy Static Site to GitHub Pages** (`deploy-pages.yml`)

**Purpose:** Manual deployment of static content to GitHub Pages with artifact tracking.

**Trigger:** Manual via `workflow_dispatch`

**Input Parameters:**
- `artifact_source` (choice)
  - `auto` - Auto-detect from: `public/`, `docs/`, `build/`, `dist/`, `website/`
  - `public` - Deploy from `public/` directory
  - `docs` - Deploy from `docs/` directory
  - `build` - Deploy from `build/` directory
  - `dist` - Deploy from `dist/` directory
  - `website` - Deploy from `website/` directory

- `retention_days` (string, default: 30)
  - How long to keep the artifact (1-90 days)

**Jobs:**

#### prepare
- Checks out repository (shallow clone: `fetch-depth: 1`)
- Auto-detects or uses specified artifact source
- Generates fallback HTML if no content found
- Uploads artifact with metadata
- Outputs: `artifact_id`, `artifact_url`, `artifact_size`

#### deploy
- Deploys artifact using official `actions/deploy-pages@v4`
- Uses artifact ID from prepare job (guarantees correct version)
- Creates deployment environment (`github-pages`)
- Generates summary report
- Outputs: `page_url`, `artifact_id`

**Features:**
✅ Artifact ID tracking - Know exactly which artifact is deployed  
✅ Shallow clone - Faster checkout  
✅ Fallback content - Never deploy empty site  
✅ File count & size reporting - Visibility into deployments  
✅ Pretty summaries - Easy to read deployment status  
✅ Minimal permissions - Security by principle of least privilege  

**Usage:**
1. Go to Actions → "Deploy Static Site to GitHub Pages"
2. Click "Run workflow"
3. Select artifact source (or use auto-detect)
4. Set retention days (optional, default 30)
5. Click "Run workflow"

**Example Output:**
```
🚀 Artifact detected in: dist/
📦 Artifact Summary:
  Files: 145
  Size: 12.3M

✅ DEPLOYMENT COMPLETE
Repository:   KomarovAI/web-crawler
Run:          42
Artifact ID:  abc123def456
Page URL:     https://komarovai.github.io/web-crawler
Status:       SUCCESS
```

---

### 2. **Deploy Pages on Push** (`pages.yml`)

**Purpose:** Automatic deployment when content changes are pushed.

**Trigger:** 
- Push to `main` branch with changes in:
  - `public/**`
  - `docs/**`
  - `build/**`
  - `dist/**`
  - `website/**`
  - `.github/workflows/deploy-pages.yml`
- Manual trigger via `workflow_dispatch`

**Features:**
✅ Path-based filtering - Only deploy when relevant files change  
✅ Single job - Fast and simple  
✅ Artifact ID integration - Reliable deployment  
✅ Automatic on every push - No manual steps required  

**Behavior:**
- No concurrency limit (allows queue of deployments)
- Uses shallow clone for speed
- Automatic status reporting

---

## 🔧 Configuration

### Setup GitHub Pages

1. Go to repository Settings → Pages
2. Select "GitHub Actions" as source
3. Save

### Environment Protection (Optional)

To require approval before deployment:

1. Settings → Environments → `github-pages`
2. Add required reviewers
3. Workflows will wait for approval

---

## 📊 Artifact Management

### Retention Policy

- Default: 30 days
- Configurable per workflow run (1-90 days)
- Automatic cleanup after retention expires

### Artifact ID

Each deployment is tied to a specific artifact ID:

```yaml
artifact_id: ${{ steps.upload.outputs.artifact-id }}
```

This guarantees that:
- ✅ Exact version is deployed
- ✅ Deployment is reproducible
- ✅ Easy to rollback (re-deploy old artifact)

---

## 🐛 Troubleshooting

### Workflow fails with "No artifacts found"

**Solution:**
- Ensure your content is in one of: `public/`, `docs/`, `build/`, `dist/`, `website/`
- Or specify the correct directory in workflow input
- Fallback page will be created if no content found

### Pages shows 404

**Check:**
1. Pages enabled in Settings
2. Source set to "GitHub Actions"
3. Workflow completed successfully
4. `index.html` exists in artifact

### Slow deployments

**Optimization:**
- Reduce artifact size (remove unnecessary files)
- Use `fetch-depth: 1` (already configured)
- Limit retention days (default 30 is good)

---

## 🔒 Security

### Minimal Permissions

Workflows only request required permissions:

```yaml
permissions:
  contents: read      # Read source code
  pages: write        # Deploy to Pages
  id-token: write     # OIDC token for deployment
```

### No Secrets Required

- Uses built-in OIDC for authentication
- No personal access tokens (PAT) needed
- No secrets exposed in logs

---

## 📈 Best Practices Applied

✅ **Semantic Versioning** - Actions pinned to major versions (@v4, @v3)  
✅ **Concurrency Control** - Prevents race conditions  
✅ **Error Handling** - `set -e` in shell scripts  
✅ **Artifact API** - Instead of cache for job-to-job data  
✅ **Output Variables** - Proper variable management with `$GITHUB_OUTPUT`  
✅ **Environment Isolation** - GitHub Pages deployment environment  
✅ **Fallback Content** - Graceful degradation if no artifacts  
✅ **Monitoring** - File count and size reporting  
✅ **Documentation** - Clear job names and descriptions  
✅ **Status Reporting** - Summary with emoji and formatting  

---

## 🔄 Workflow Comparison

| Feature | deploy-pages.yml | pages.yml |
|---------|------------------|----------|
| Trigger | Manual | Automatic (push) |
| Input selection | Yes | No (auto) |
| Job count | 2 (prepare + deploy) | 1 |
| Concurrency | No cancel | Queue-based |
| Use case | Selective deploy | Every push |

---

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [GitHub Pages Guide](https://docs.github.com/pages)
- [Deploy Pages Action](https://github.com/actions/deploy-pages)
- [Upload Pages Artifact](https://github.com/actions/upload-pages-artifact)

---

*Last updated: 2025-12-26*
