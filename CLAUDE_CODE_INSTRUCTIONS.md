# Instructions for Claude Code

## Quick Start (Copy-Paste This)

```
Extract the tarball, navigate into the directory, and deploy to GitHub:

tar xzf pm10_audit_github_repo.tar.gz
cd pm10_audit_repo

# Make sure GitHub CLI is installed and authenticated
gh auth login

# Deploy to GitHub (creates repo, pushes code, creates release)
./deploy_to_github.sh

# Verify everything works
./verify_deployment.sh
```

## What These Scripts Do

### deploy_to_github.sh
1. Checks you're in the right directory
2. Verifies `gh` (GitHub CLI) is installed
3. Checks GitHub authentication
4. Initializes git if needed
5. Creates public repo `pm10-validation-audit`
6. Pushes all code
7. Creates tag v1.0.0
8. Creates GitHub release with notes

### verify_deployment.sh
1. Tests Python version (3.11+)
2. Checks all dependencies installed
3. Runs screening script → verifies output
4. Runs benchmark script → verifies output  
5. Checks git remote configured
6. Checks tag v1.0.0 exists and pushed

## Expected Output

After running both scripts successfully, you'll have:

✅ GitHub repository at: `https://github.com/YOUR_USERNAME/pm10-validation-audit`  
✅ Release v1.0.0 tagged and published  
✅ All scripts tested and working  
✅ Ready for Zenodo DOI minting

## Troubleshooting

**"gh: command not found"**
```bash
# macOS:
brew install gh

# Ubuntu/Debian:
sudo apt install gh

# Windows (WSL):
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list
sudo apt update
sudo apt install gh
```

**"gh auth login required"**
```bash
gh auth login
# Select: GitHub.com
# Select: HTTPS
# Authenticate in browser
```

**"Repository already exists"**

If you need to delete and recreate:
```bash
gh repo delete pm10-validation-audit --yes
./deploy_to_github.sh
```

**"Python dependencies missing"**
```bash
pip install -r requirements.txt
# or
pip install numpy pandas matplotlib scikit-learn scipy openpyxl
```

## After Deployment: Get Zenodo DOI

1. **Go to Zenodo:**  
   https://zenodo.org/account/settings/github

2. **Sign in with GitHub** (if not already)

3. **Sync repositories:**  
   Click "Sync now" button

4. **Find your repo:**  
   Scroll to find `pm10-validation-audit`

5. **Toggle ON:**  
   Flip the switch to enable Zenodo archiving

6. **Wait 5 minutes:**  
   Zenodo will detect the v1.0.0 release and create a DOI

7. **Get the DOI:**  
   Refresh the page → DOI appears next to your repo  
   Format: `10.5281/zenodo.XXXXXXX` (7 digits)

8. **Update paper:**  
   Edit `code_availability.tex`:
   ```latex
   \url{https://github.com/YOUR_USERNAME/pm10-validation-audit}
   DOI: \url{https://doi.org/10.5281/zenodo.XXXXXXX}
   ```

9. **Update README badge:**  
   ```bash
   # In the repo directory
   sed -i 's/zenodo.XXXXXXX/zenodo.1234567/g' README.md
   git add README.md
   git commit -m "Add Zenodo DOI badge"
   git push
   ```

## Full Command Sequence

```bash
# 1. Extract and navigate
tar xzf pm10_audit_github_repo.tar.gz
cd pm10_audit_repo

# 2. Authenticate GitHub CLI (one-time)
gh auth login

# 3. Deploy
./deploy_to_github.sh

# 4. Verify
./verify_deployment.sh

# 5. Get Zenodo DOI (manual steps above)

# 6. Update README with DOI
sed -i 's/zenodo.XXXXXXX/zenodo.1234567/g' README.md
git add README.md
git commit -m "Add Zenodo DOI badge"
git push
```

Done! ✅
