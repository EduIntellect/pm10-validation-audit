#!/bin/bash
# GitHub Repository Deployment Script for Claude Code
# Run this from inside the pm10_audit_repo/ directory

set -e  # Exit on any error

echo "=================================================="
echo "PM10 Validation Audit - GitHub Deployment"
echo "=================================================="
echo ""

# Check we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "screening" ]; then
    echo "❌ ERROR: Must run this from pm10_audit_repo/ directory"
    echo "   Current directory: $(pwd)"
    exit 1
fi

echo "✓ Verified we're in pm10_audit_repo/"
echo ""

# Check GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ ERROR: GitHub CLI (gh) not installed"
    echo "   Install: https://cli.github.com/"
    echo "   Or: brew install gh  (macOS)"
    echo "   Or: sudo apt install gh  (Ubuntu)"
    exit 1
fi

echo "✓ GitHub CLI found"
echo ""

# Check authentication
echo "Checking GitHub authentication..."
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub"
    echo "   Run: gh auth login"
    echo "   Then run this script again"
    exit 1
fi

echo "✓ GitHub authenticated"
echo ""

# Get GitHub username
GH_USER=$(gh api user -q .login)
echo "✓ Authenticated as: $GH_USER"
echo ""

# Prompt for confirmation
read -p "Create public repo 'pm10-validation-audit' for user '$GH_USER'? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: PM10 validation audit repository

This repository contains all code and data supporting the systematic audit 
of temporal validation practices in PM10 forecasting literature.

García Crespi, F., Yubero Funes, E., & Alfosea Simón, M. (2026).
Operational Predictability Limits in Multi-Step PM10 Forecasting: 
A Systematic Audit and Reproducible Evaluation Framework for Temporal Validation.
Environmental Modelling & Software (submitted)."
    
    echo "✓ Git initialized and initial commit created"
else
    echo "✓ Git already initialized"
fi

echo ""

# Create GitHub repository
echo "Creating GitHub repository..."
gh repo create pm10-validation-audit \
    --public \
    --description "Code and data for García Crespi et al. (2026) systematic audit of PM10 forecasting validation practices" \
    --source=. \
    --push

echo ""
echo "✓ Repository created and pushed to GitHub"
echo "  URL: https://github.com/$GH_USER/pm10-validation-audit"
echo ""

# Create release tag for Zenodo
echo "Creating release v1.0.0 for Zenodo..."
git tag -a v1.0.0 -m "Publication release

Repository snapshot for paper submission to Environmental Modelling & Software.

This release corresponds to:
García Crespi, F., Yubero Funes, E., & Alfosea Simón, M. (2026).
Operational Predictability Limits in Multi-Step PM10 Forecasting: 
A Systematic Audit and Reproducible Evaluation Framework for Temporal Validation.

All analyses are fully reproducible using the scripts in screening/ and benchmark/."

git push origin v1.0.0

echo ""
echo "✓ Release v1.0.0 created and pushed"
echo ""

# Create GitHub release
echo "Creating GitHub release..."
gh release create v1.0.0 \
    --title "Publication release (García Crespi et al. 2026)" \
    --notes "Repository snapshot for paper submission to *Environmental Modelling & Software*.

## Citation

García Crespi, F., Yubero Funes, E., & Alfosea Simón, M. (2026). 
Operational Predictability Limits in Multi-Step PM₁₀ Forecasting: 
A Systematic Audit and Reproducible Evaluation Framework for Temporal Validation. 
*Environmental Modelling & Software* (submitted).

## Contents

- \`screening/\` — Lexical screening pipeline (Section 2.2)
- \`benchmark/\` — H* synthetic benchmark (Section 3.5)  
- \`audit/\` — Full-text audit forms and metadata (Section 2.3-2.4)
- \`data/\` — Scopus corpus metadata and audit results

## Reproducibility

All analyses are fully reproducible:

\`\`\`bash
pip install -r requirements.txt
cd screening && python run_screening.py
cd ../benchmark && python hstar_demo.py
\`\`\`

## Zenodo DOI

After enabling Zenodo integration, a DOI will be automatically minted for this release within ~5 minutes.

## License

Code: MIT | Data: CC BY 4.0"

echo ""
echo "=================================================="
echo "✅ DEPLOYMENT COMPLETE"
echo "=================================================="
echo ""
echo "Repository URL:"
echo "  https://github.com/$GH_USER/pm10-validation-audit"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate Zenodo integration:"
echo "   → Go to: https://zenodo.org/account/settings/github"
echo "   → Click 'Sync now'"
echo "   → Find 'pm10-validation-audit' and toggle ON"
echo "   → Wait ~5 minutes for DOI to be minted"
echo ""
echo "2. Get your Zenodo DOI:"
echo "   → Go to: https://zenodo.org/account/settings/github"
echo "   → Find your repository"
echo "   → Copy DOI (will be: 10.5281/zenodo.XXXXXXX)"
echo ""
echo "3. Update paper LaTeX:"
echo "   → Edit code_availability.tex"
echo "   → Replace placeholder with:"
echo "     \\\\url{https://github.com/$GH_USER/pm10-validation-audit}"
echo "     DOI: \\\\url{https://doi.org/10.5281/zenodo.XXXXXXX}"
echo ""
echo "4. Update repository README badge:"
echo "   → Edit README.md"
echo "   → Replace zenodo.XXXXXXX with your actual DOI"
echo "   → Commit and push"
echo ""
echo "=================================================="
