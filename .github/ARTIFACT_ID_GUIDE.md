# Artifact ID Tracking Guide

## What is Artifact ID?

Artifact ID is a unique identifier for each uploaded artifact in GitHub Actions. It ensures:

- ✅ **Exact traceability** - Know what was deployed
- ✅ **Reproducibility** - Deploy exact version anytime
- ✅ **Rollback capability** - Revert to previous deployments
- ✅ **Audit trail** - Full deployment history

---

## How It Works

### Upload Phase

```yaml
- name: Upload Pages artifact
  id: upload
  uses: actions/upload-pages-artifact@v3
  with:
    path: _site

# Output: artifact-id = abc123def456789...
```

### Output Phase

Capture the artifact ID:
```yaml
outputs:
  artifact_id: ${{ steps.upload.outputs.artifact-id }}
```

### Deploy Phase

Use the specific artifact:
```yaml
- name: Deploy
  uses: actions/deploy-pages@v4
  with:
    artifact_id: ${{ needs.prepare.outputs.artifact_id }}  # Specific version
```

---

## Deployment Flow

```
🃁 Checkout Code
        ↓
📦 Prepare Artifacts
        ↓
💫 Get artifact-id: abc123def456
        ↓
🚀 Pass to deploy job
        ↓
🔍 Find exact artifact (abc123def456)
        ↓
🌐 Deploy to Pages
        ↓
✅ Live (reproducible)
```

---

## Practical Examples

### Example 1: Check What Was Deployed

1. Go to **Actions** tab
2. Click failed or successful workflow run
3. Click **prepare** job
4. Find log line:
   ```
   📌 Artifact Information:
     ID: sha256:abc123def456789abcdef...
   ```
5. This ID is what was deployed!

### Example 2: Rollback to Previous Deployment

1. Find old workflow run in Actions
2. Note its artifact ID from logs
3. Manually trigger deploy with that ID:
   ```bash
   # If you build custom workflow:
   artifact_id: sha256:abc123def456789abcdef...
   ```
4. Deploy to restore previous state

### Example 3: Track Deployment in Logs

```log
📌 Artifact Information:
  ID: sha256:7fbd7d651c4d03c4ed305a748490def4f95b24e3a26e23a73c1925b41a4bfe95
  URL: https://api.github.com/repos/KomarovAI/web-crawler/actions/artifacts/4959324257
  Size: 152 MB

✅ DEPLOYMENT COMPLETE
Repository:   KomarovAI/web-crawler
Run:          42
Artifact ID:  sha256:7fbd7d651c4d03c4ed305a748490def4f95b24e3a26e23a73c1925b41a4bfe95
Page URL:     https://komarovai.github.io/web-crawler
Status:       SUCCESS
```

---

## Why Artifact ID is Better Than Cache

### ❌ Old Approach (Cache)
```yaml
- uses: actions/cache@v4
  with:
    key: build-cache-${{ github.run_id }}
    # ⚠️ Problems:
    # - Cache not guaranteed (auto-eviction)
    # - Different key per run (defeats purpose)
    # - Slow inter-job transfer
    # - No artifact tracking
```

### ✅ New Approach (Artifact ID)
```yaml
- uses: actions/upload-pages-artifact@v3
- id: upload
  # ✅ Benefits:
  # - Guaranteed (stored in GitHub)
  # - Unique, traceable ID
  # - Direct deployment support
  # - Full audit trail
  # - Can rollback anytime
```

---

## Retention Management

### View Artifact
1. Actions tab → Workflow run
2. Scroll to **Artifacts** section
3. See:
   - Name
   - Size
   - Digest (ID)
   - Download link

### Artifact Lifetime

| Setting | Default | Range | Notes |
|---------|---------|-------|-------|
| Retention | 30 days | 1-90 | Auto-deleted after |
| Size limit | - | 400 MB | Per repo limit |
| Count limit | Unlimited | - | Total artifacts |

### Extend Retention

```yaml
with:
  retention-days: 90  # Max value
```

### Download Artifact

```bash
# GitHub CLI
gh run download 20479494022 -n site_archive-20479494022

# Web UI
# Actions → Run → Artifacts → Download
```

---

## API Access

### Get Artifact Info

```bash
curl -H "Authorization: token $TOKEN" \
  https://api.github.com/repos/OWNER/REPO/actions/artifacts
```

Response:
```json
{
  "artifacts": [
    {
      "id": 4959324257,
      "name": "site_archive-20479494022",
      "size_in_bytes": 159383552,
      "created_at": "2025-12-26T10:30:51Z",
      "expires_at": "2026-01-25T10:30:51Z"
    }
  ]
}
```

---

## Best Practices

### ✅ Do
- 📌 Always capture artifact-id in outputs
- 🚦 Pass artifact-id between jobs
- 📁 Reference in deploy step
- 🔍 Log artifact ID for records
- 📊 Document deployment versions

### ❌ Don't
- ❌ Hardcode artifact IDs
- ❌ Use cache for inter-job data
- ❌ Rely on filename alone
- ❌ Skip artifact verification
- ❌ Deploy without tracking

---

## Troubleshooting

### Artifact ID Not Found

```bash
Error: artifact-id not available
```

**Fix:**
1. Check `uses: actions/upload-pages-artifact@v3` is present
2. Verify `id: upload` is set
3. Check output is captured in needs

### Deployment with Wrong Artifact

**Prevent:**
```yaml
# ❌ Wrong
artifact_id: some-hardcoded-id

# ✅ Correct
artifact_id: ${{ needs.prepare.outputs.artifact_id }}
```

### Lost Artifact ID

**Recover:**
1. Check workflow run logs
2. Find line: "Artifact Information:"
3. Copy ID from there
4. Use in manual deployment

---

## Summary

| Aspect | Value | Benefit |
|--------|-------|----------|
| **Tracking** | Unique SHA256 | Know exact version |
| **Reliability** | GitHub-backed | Never lost |
| **Reproducibility** | Immutable | Deploy anytime |
| **Audit** | Full history | Compliance ready |
| **Rollback** | 1-click | Fast recovery |

---

*For more details, see [WORKFLOWS.md](./WORKFLOWS.md)*
