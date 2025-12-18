# GitHub Secrets Setup - Archive v5.2

## Two Deployment Modes

### Mode 1: CRAWL (New Archive)
- **Use when**: First time capturing website or need fresh data
- **Time**: ~2 hours
- **Steps**: Crawl → Archive → Deploy

### Mode 2: REUSE (Quick Redeploy)
- **Use when**: Need to redeploy to different repo or fix deploy logic
- **Time**: ~5 minutes
- **Steps**: Skip crawl → Reuse artifact → Deploy

## Setup Instructions

### Step 1: Create Fine-Grained PAT
https://github.com/settings/personal-access-tokens/new

- **Token name**: web-crawler-deployment
- **Expiration**: 90 days
- **Repository access**: Select repositories (target repo)
- **Permissions**: Contents - Read and write

### Step 2: Add Secret
https://github.com/KomarovAI/web-crawler/settings/secrets/actions

- **Name**: EXTERNAL_REPO_PAT
- **Value**: (paste token)

### Step 3: Run Workflow

**CRAWL Mode:**
```
Actions → Archive v5.2 → Run workflow
- url: https://example.com
- max_pages: 50
- target_repo: your-username/archive-repo
- reuse_artifact_run_id: (leave empty)
```

**REUSE Mode:**
```
Actions → Archive v5.2 → Run workflow
- url: (any value, not used)
- max_pages: 1
- target_repo: your-username/new-repo
- reuse_artifact_run_id: 20328733763 (previous run ID)
```

## Full Documentation

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete guide.
See [README_SECRETS.md](./README_SECRETS.md) for quick reference.
