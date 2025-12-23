#!/bin/bash
# Test script for orphan gh-pages branch creation
# Usage: ./scripts/test-orphan-branch.sh /path/to/test/repo

set -e

if [ -z "$1" ]; then
  TEST_DIR="/tmp/test-orphan-pages"
else
  TEST_DIR="$1"
fi

echo "📂 Initializing test repository at: $TEST_DIR"

rm -rf "$TEST_DIR" 2>/dev/null || true
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

git init
git config user.email "test@test.com"
git config user.name "Test User"

# Create initial commit on main
echo "Test content" > README.md
git add README.md
git commit -m "Initial commit"

echo "👀 Initial state:"
echo "  Branches: $(git branch -a)"
echo "  .git exists: $(test -d .git && echo '✅ yes' || echo '❌ no')"

# Test: Create orphan branch and clean without destroying .git
echo "
📄 Creating orphan gh-pages branch..."
git checkout --orphan gh-pages

echo "⚠️  Before cleanup:"
echo "  Files: $(ls -la | wc -l)"
echo "  .git exists: $(test -d .git && echo '✅ yes' || echo '❌ no')"

# Clean tracked files
echo "📄 Running: git rm -rf ."
git rm -rf . 2>/dev/null || true

# Remove untracked files but preserve .git
echo "📄 Removing untracked files (preserving .git)..."
find . -maxdepth 1 \
  -not -name '.git' \
  -not -name '.' \
  -not -name '..' \
  \( -type f -o -type d \) \
  -exec rm -rf {} + 2>/dev/null || true

echo "👀 After cleanup:"
echo "  Files: $(ls -la | wc -l)"
echo "  .git exists: $(test -d .git && echo '✅ yes' || echo '❌ no')"

if [ ! -d .git ]; then
  echo "❌ FATAL: .git directory was removed!"
  exit 1
fi

# Create .nojekyll and commit
echo "📄 Creating .nojekyll marker..."
touch .nojekyll
git add .nojekyll

echo "📝 Committing..."
git commit -m "chore: Initialize gh-pages branch" --allow-empty

echo "✅ SUCCESS! Orphan branch created correctly"
echo "📁 Final state:"
echo "  Current branch: $(git branch --show-current)"
echo "  .git exists: ✅ yes"
echo "  Files in working dir: $(find . -not -path './.git/*' -type f | wc -l)"
echo ""
echo "🗑️  Cleaning up test directory..."
cd /
rm -rf "$TEST_DIR"
echo "🙋 All tests passed!"
