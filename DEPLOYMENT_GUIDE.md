# Git Deployment Guide

This guide will help you deploy your NLP to SQL application to GitHub.

---

## Prerequisites

- Git installed on your machine
- GitHub account
- OpenRouter API key

---

## Step 1: Initialize Git Repository

```bash
cd "/Users/arushigupta/Desktop/EMB/Demos/NLP to SQL"
git init
```

---

## Step 2: Configure Git (First Time Only)

Set your Git identity:

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

To set these globally (for all repositories):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Step 3: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and log in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Enter repository details:
   - **Name**: `nlp-to-sql-chat-app` (or your preferred name)
   - **Description**: "NLP to SQL Chat Application with Professional Reports"
   - **Visibility**: Choose Public or Private
   - **Do NOT** initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"

---

## Step 4: Prepare Your Code for Deployment

### A. Check Your .env File

**IMPORTANT**: Never commit your `.env` file with real API keys!

Your `.env` file is already in `.gitignore`, which means it won't be pushed to Git.

Verify sensitive data is excluded:

```bash
git status
# Make sure .env is NOT listed in the files to be committed
```

### B. Review What Will Be Committed

```bash
git status
```

This will show all files that will be included.

---

## Step 5: Stage and Commit Your Files

### Stage all files:

```bash
git add .
```

### Check what's staged:

```bash
git status
```

### Create your first commit:

```bash
git commit -m "Initial commit: NLP to SQL Chat Application with professional reports"
```

---

## Step 6: Connect to GitHub and Push

After creating your GitHub repository, you'll see instructions. Follow these:

### Add the remote repository:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repository name.

### Rename branch to main (if needed):

```bash
git branch -M main
```

### Push your code:

```bash
git push -u origin main
```

You'll be prompted to enter your GitHub credentials. For password, use a **Personal Access Token** (PAT) instead of your actual password.

---

## Step 7: Create Personal Access Token (PAT)

If you don't have a PAT:

1. Go to GitHub.com → Settings → Developer settings
2. Click "Personal access tokens" → "Tokens (classic)"
3. Click "Generate new token" → "Generate new token (classic)"
4. Give it a name: "NLP to SQL App"
5. Select scopes:
   - ✅ **repo** (full control of private repositories)
6. Click "Generate token"
7. **Copy the token immediately** (you won't see it again!)
8. Use this token as your password when pushing to GitHub

---

## Step 8: Verify Deployment

1. Go to your GitHub repository URL
2. You should see all your files
3. Verify that `.env` is NOT in the repository (security check)

---

## For Team Members / New Setup

When someone clones your repository, they need to:

### 1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file:

```bash
cp .env.example .env
```

Then edit `.env` and add their own API keys:

```
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
OPENROUTER_MODEL=openai/gpt-4-turbo
COMPANY_NAME=Business Intelligence
```

### 5. Add sample data:

Place Excel/CSV files in the `data/` directory.

### 6. Run the application:

```bash
streamlit run app.py
```

---

## Common Git Commands

### After making changes:

```bash
# See what changed
git status

# Stage specific files
git add filename.py

# Stage all changes
git add .

# Commit with message
git commit -m "Description of changes"

# Push to GitHub
git push
```

### Create a new feature branch:

```bash
# Create and switch to new branch
git checkout -b feature/new-feature-name

# Make your changes, then commit
git add .
git commit -m "Add new feature"

# Push branch to GitHub
git push -u origin feature/new-feature-name
```

### Pull latest changes:

```bash
git pull origin main
```

---

## Deployment to Cloud Platforms

### Option 1: Deploy to Streamlit Cloud (FREE)

1. Push your code to GitHub (Steps 1-6 above)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository and branch
6. Set main file: `app.py`
7. Click "Advanced settings" and add environment variables:
   ```
   OPENROUTER_API_KEY=sk-or-v1-your-key
   OPENROUTER_MODEL=openai/gpt-4-turbo
   COMPANY_NAME=Business Intelligence
   ```
8. Click "Deploy"

**Note**: You'll need to upload your data files after deployment or modify the app to accept file uploads.

### Option 2: Deploy to Heroku

1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: sh setup.sh && streamlit run app.py
   ```
3. Create `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "[server]
   headless = true
   port = $PORT
   enableCORS = false
   " > ~/.streamlit/config.toml
   ```
4. Deploy:
   ```bash
   heroku login
   heroku create your-app-name
   heroku config:set OPENROUTER_API_KEY=your-key
   git push heroku main
   ```

### Option 3: Deploy to AWS / Azure / GCP

Requires more advanced setup with Docker containers or VM instances.

---

## Security Best Practices

1. **Never commit `.env` files** with real API keys
2. **Use `.gitignore`** to exclude sensitive files
3. **Use environment variables** for all secrets
4. **Rotate API keys** if accidentally committed
5. **Review commits** before pushing to ensure no secrets

### If you accidentally committed secrets:

```bash
# Remove file from Git history
git rm --cached .env
git commit -m "Remove .env from repository"

# Force push (use with caution!)
git push -f origin main

# Then rotate your API keys immediately!
```

---

## Troubleshooting

### Problem: `git push` asks for password repeatedly

**Solution**: Use SSH instead of HTTPS

1. Generate SSH key:
   ```bash
   ssh-keygen -t ed25519 -C "your.email@example.com"
   ```
2. Add to GitHub: Settings → SSH and GPG keys → New SSH key
3. Change remote URL:
   ```bash
   git remote set-url origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
   ```

### Problem: Large files won't push

**Solution**: Use Git LFS for files > 50MB

```bash
git lfs install
git lfs track "*.xlsx"
git lfs track "*.db"
git add .gitattributes
git commit -m "Add Git LFS"
```

### Problem: Merge conflicts

**Solution**:

```bash
# Pull latest changes
git pull origin main

# Resolve conflicts in your editor
# Look for <<<<<, =====, >>>>> markers

# After resolving:
git add .
git commit -m "Resolve merge conflicts"
git push
```

---

## Complete Deployment Checklist

- [ ] Git installed and configured
- [ ] GitHub account created
- [ ] Repository created on GitHub
- [ ] `.env` file in `.gitignore`
- [ ] Code committed locally
- [ ] Remote repository connected
- [ ] Code pushed to GitHub
- [ ] `.env` NOT in repository (verified)
- [ ] README.md updated with setup instructions
- [ ] Team members can clone and run the app

---

## Quick Reference: Deploy to GitHub

```bash
# Navigate to project directory
cd "/Users/arushigupta/Desktop/EMB/Demos/NLP to SQL"

# Initialize Git
git init

# Configure Git (first time only)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Stage all files
git add .

# Create first commit
git commit -m "Initial commit: NLP to SQL Chat Application"

# Add GitHub remote (replace with your repository URL)
git remote add origin https://github.com/YOUR_USERNAME/nlp-to-sql-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Support

- **Git Documentation**: https://git-scm.com/doc
- **GitHub Guides**: https://guides.github.com
- **Streamlit Cloud Docs**: https://docs.streamlit.io/streamlit-community-cloud

---

**Generated**: 2026-01-09
**Status**: Ready for deployment
