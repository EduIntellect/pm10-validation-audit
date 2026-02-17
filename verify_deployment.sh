#!/bin/bash
# Post-deployment verification script
# Run this AFTER deploy_to_github.sh to verify everything works

set -e

echo "=================================================="
echo "PM10 Validation Audit - Verification Tests"
echo "=================================================="
echo ""

# Test 1: Check Python version
echo "Test 1: Python version"
PYTHON_VERSION=$(python3 --version | grep -oP '\d+\.\d+')
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 11 ]; then
    echo "  ✓ Python $PYTHON_VERSION (>=3.11 required)"
else
    echo "  ⚠ Python $PYTHON_VERSION (3.11+ recommended)"
fi
echo ""

# Test 2: Check dependencies
echo "Test 2: Python dependencies"
MISSING=0
for pkg in numpy pandas matplotlib sklearn scipy; do
    if python3 -c "import $pkg" 2>/dev/null; then
        echo "  ✓ $pkg installed"
    else
        echo "  ✗ $pkg missing"
        MISSING=1
    fi
done

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "  Install missing packages:"
    echo "    pip install -r requirements.txt"
    exit 1
fi
echo ""

# Test 3: Run screening script
echo "Test 3: Lexical screening pipeline"
cd screening
if python3 run_screening.py > /tmp/screening_test.log 2>&1; then
    if [ -f "screening_results.csv" ] && [ -f "prevalence_summary.txt" ]; then
        ROWS=$(wc -l < screening_results.csv)
        echo "  ✓ Script executed successfully"
        echo "  ✓ Generated screening_results.csv ($ROWS rows)"
        echo "  ✓ Generated prevalence_summary.txt"
    else
        echo "  ✗ Script ran but didn't generate expected files"
        exit 1
    fi
else
    echo "  ✗ Script failed (see /tmp/screening_test.log)"
    exit 1
fi
cd ..
echo ""

# Test 4: Run benchmark script
echo "Test 4: H* benchmark"
cd benchmark
if python3 hstar_demo.py > /tmp/benchmark_test.log 2>&1; then
    if [ -f "hstar_results.csv" ] && [ -f "figure4_hstar_comparison.png" ]; then
        ROWS=$(wc -l < hstar_results.csv)
        echo "  ✓ Script executed successfully"
        echo "  ✓ Generated hstar_results.csv ($ROWS rows)"
        echo "  ✓ Generated figure4_hstar_comparison.png"
    else
        echo "  ✗ Script ran but didn't generate expected files"
        exit 1
    fi
else
    echo "  ✗ Script failed (see /tmp/benchmark_test.log)"
    exit 1
fi
cd ..
echo ""

# Test 5: Check GitHub remote
echo "Test 5: GitHub remote configuration"
if git remote -v | grep -q "pm10-validation-audit"; then
    REMOTE_URL=$(git remote get-url origin)
    echo "  ✓ GitHub remote configured"
    echo "    $REMOTE_URL"
else
    echo "  ✗ No GitHub remote found"
    echo "    Run deploy_to_github.sh first"
    exit 1
fi
echo ""

# Test 6: Check git tag
echo "Test 6: Release tag v1.0.0"
if git tag | grep -q "v1.0.0"; then
    echo "  ✓ Tag v1.0.0 exists"
    if git ls-remote --tags origin | grep -q "v1.0.0"; then
        echo "  ✓ Tag pushed to GitHub"
    else
        echo "  ⚠ Tag exists locally but not on GitHub"
    fi
else
    echo "  ✗ Tag v1.0.0 not found"
    echo "    Run deploy_to_github.sh first"
    exit 1
fi
echo ""

# Summary
echo "=================================================="
echo "✅ ALL VERIFICATION TESTS PASSED"
echo "=================================================="
echo ""
echo "Repository is ready for Zenodo integration."
echo ""
echo "Next: Enable Zenodo"
echo "  1. Go to: https://zenodo.org/account/settings/github"
echo "  2. Click 'Sync now'"
echo "  3. Toggle ON for 'pm10-validation-audit'"
echo "  4. Wait ~5 minutes for DOI"
echo ""
