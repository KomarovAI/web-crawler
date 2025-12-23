# GitHub Pages Deployment Fix

**Problem:** Workflow failed with `fatal: not a git repository` when creating orphan `gh-pages` branch.

**Root Cause:** The cleanup command `git rm -rf . && rm -rf * .*` was destroying the `.git` directory, making it impossible to run subsequent git operations.

## Fixed Issues

### 1. Orphan Branch Initialization ✅

**Before (broken):**
```bash
git checkout --orphan gh-pages
git rm -rf . 2>/dev/null || true
rm -rf * .* 2>/dev/null || true  # ❌ Destroys .git

git commit -m "..." --allow-empty  # 💥 FAILS: no .git found
```

**After (fixed):**
```bash
git checkout --orphan gh-pages

# Remove tracked files
git rm -rf . 2>/dev/null || true

# Remove untracked files BUT preserve .git
find . -maxdepth 1 \
  -not -name '.git' \
  -not -name '.' \
  -not -name '..' \
  \( -type f -o -type d \) \
  -exec rm -rf {} + 2>/dev/null || true

git commit -m "..." --allow-empty  # ✅ Works: .git is intact
```

### 2. WARC File Cleanup ✅

Added `.git` exclusion to prevent scanning inside git metadata:
```bash
# Before: find . -type f \( -name "*.warc" -o -name "*.warc.gz" \)
find . -type f \( -name "*.warc" -o -name "*.warc.gz" \) ! -path './.git/*'  # ✅ After
```

### 3. File Counting ✅

Exclude `.git` from deployment metrics:
```bash
# Count files
find "$TARGET_DIR" -type f ! -path './.git/*' | wc -l
```

## Files Modified

| File | Changes |
|------|----------|
| `.github/workflows/deploy-pages.yml` | Fixed orphan branch init, added `.git` exclusions |
| `scripts/test-orphan-branch.sh` | New: test script for local validation |

## Testing

### Local Test (Before Deployment)
```bash
bash scripts/test-orphan-branch.sh
```

Output example:
```
✅ SUCCESS! Orphan branch created correctly
📁 Final state:
  Current branch: gh-pages
  .git exists: ✅ yes
  Files in working dir: 1
```

## Workflow Execution

1. ✅ Create orphan branch (preserves `.git`)
2. ✅ Clean working directory (safe removal)
3. ✅ Copy archive contents
4. ✅ Rewrite URLs (Python script)
5. ✅ Commit and force push

## Performance

- **Time complexity:** O(n) where n = archive file count
- **Memory:** O(1) - streaming operations
- **Git overhead:** Minimal (orphan branch has no parents)

## References

- [Git orphan branches documentation](https://git-scm.com/docs/git-checkout#Documentation/git-checkout.txt---orphan)
- [GitHub Pages gh-pages branch deployment](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#static-site-generators)
- [Shell find command](https://man7.org/linux/man-pages/man1/find.1.html)
