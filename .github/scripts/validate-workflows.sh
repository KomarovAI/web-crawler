#!/bin/bash

# Validate GitHub Actions Workflows
# This script checks YAML syntax and basic structure

set -e

echo "🔍 Validating GitHub Actions workflows..."
echo ""

WORKFLOW_DIR=".github/workflows"
ERROR_COUNT=0

# Check if workflows directory exists
if [ ! -d "$WORKFLOW_DIR" ]; then
    echo "❌ Workflows directory not found: $WORKFLOW_DIR"
    exit 1
fi

# Function to validate YAML
validate_yaml() {
    local file=$1
    echo "🔎 Checking: $file"
    
    if command -v yamllint &> /dev/null; then
        if ! yamllint -d relaxed "$file" 2>/dev/null; then
            echo "❌ YAML syntax error in $file"
            ((ERROR_COUNT++))
            return 1
        fi
    else
        # Fallback: basic Python YAML validation
        if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            echo "❌ YAML syntax error in $file"
            ((ERROR_COUNT++))
            return 1
        fi
    fi
    
    # Check for required fields
    if ! grep -q "^name:" "$file"; then
        echo "⚠️  Missing 'name' field in $file"
        ((ERROR_COUNT++))
        return 1
    fi
    
    if ! grep -q "^on:" "$file"; then
        echo "⚠️  Missing 'on' trigger in $file"
        ((ERROR_COUNT++))
        return 1
    fi
    
    if ! grep -q "^jobs:" "$file"; then
        echo "⚠️  Missing 'jobs' section in $file"
        ((ERROR_COUNT++))
        return 1
    fi
    
    echo "✅ Valid"
    return 0
}

# Validate all workflow files
for workflow in "$WORKFLOW_DIR"/*.yml "$WORKFLOW_DIR"/*.yaml; do
    if [ -f "$workflow" ]; then
        validate_yaml "$workflow"
        echo ""
    fi
done

# Summary
echo "📋 Summary"
echo "========================================"

if [ "$ERROR_COUNT" -eq 0 ]; then
    echo "✅ All workflows are valid!"
    exit 0
else
    echo "❌ Found $ERROR_COUNT error(s)"
    exit 1
fi
