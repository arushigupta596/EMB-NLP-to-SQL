# Quick Deploy to GitHub - 5 Minutes

Follow these steps to deploy your NLP to SQL application to GitHub in 5 minutes.

---

## Prerequisites

- GitHub account: [Sign up here](https://github.com/signup)
- Git installed: Check with `git --version`

---

## Step-by-Step

### 1. Create GitHub Repository (2 minutes)

1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `nlp-to-sql-app`
   - **Description**: "NLP to SQL Chat with Professional Reports"
   - **Public** or **Private**: Your choice
   - **Do NOT check**: Initialize with README
3. Click **"Create repository"**
4. Keep this page open - you'll need the URL

---

### 2. Configure Git (1 minute - first time only)

Open terminal and run:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

### 3. Deploy Your Code (2 minutes)

Open terminal and navigate to your project:

```bash
cd "/Users/arushigupta/Desktop/EMB/Demos/NLP to SQL"
```

Run these commands one by one:

```bash
# Initialize Git
git init

# Stage all files
git add .

# Create first commit
git commit -m "Initial commit: NLP to SQL with professional reports"

# Add GitHub remote (replace with YOUR repository URL from step 1)
git remote add origin https://github.com/YOUR_USERNAME/nlp-to-sql-app.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

**When prompted for credentials**:
- Username: Your GitHub username
- Password: Use a **Personal Access Token** (see below)

---

### 4. Create Personal Access Token (if needed)

If you don't have a token:

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Name: `NLP to SQL App`
4. Select scopes: Check **"repo"**
5. Click **"Generate token"**
6. **Copy the token** (starts with `ghp_`)
7. Use this as your password when pushing

---

## Alternative: Use the Script

We've created an automated script for you:

```bash
cd "/Users/arushigupta/Desktop/EMB/Demos/NLP to SQL"
./deploy_to_github.sh
```

This script will guide you through the process interactively.

---

## Verify Deployment

1. Go to your GitHub repository URL
2. You should see all your files
3. **Important**: Verify `.env` is NOT visible (security check)

---

## What Gets Deployed

✅ **Included**:
- All Python code (`.py` files)
- Configuration files
- Documentation (`.md` files)
- Requirements (`requirements.txt`)
- Sample questions
- `.env.example` (template)

❌ **Excluded** (by `.gitignore`):
- `.env` file with your API keys
- Database files (`.db`, `.sqlite`)
- Generated reports (`.pdf`)
- Virtual environment (`venv/`)
- Python cache (`__pycache__/`)

---

## After Deployment

Share your repository with your team:

```
https://github.com/YOUR_USERNAME/nlp-to-sql-app
```

Team members can clone and set up:

```bash
git clone https://github.com/YOUR_USERNAME/nlp-to-sql-app.git
cd nlp-to-sql-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with their API keys
streamlit run app.py
```

---

## Troubleshooting

### Error: "remote origin already exists"

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/nlp-to-sql-app.git
```

### Error: "authentication failed"

Use a Personal Access Token instead of your password (see Step 4 above).

### Error: "src refspec main does not match any"

```bash
git branch -M main
git push -u origin main
```

---

## Next Steps

- [ ] Deploy to Streamlit Cloud (FREE): See DEPLOYMENT_GUIDE.md
- [ ] Add collaborators to your GitHub repo
- [ ] Set up GitHub Actions for CI/CD
- [ ] Configure branch protection rules

---

## Need Help?

See **DEPLOYMENT_GUIDE.md** for detailed instructions and cloud deployment options.

---

**Generated**: 2026-01-09
**Estimated Time**: 5 minutes
**Difficulty**: Easy
