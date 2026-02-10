# Secure Deployment Guide for NLP to SQL Application

## Overview
This guide explains how to deploy your NLP to SQL application to Streamlit Community Cloud without exposing API keys or sensitive information.

---

## ⚠️ CRITICAL: Securing API Keys

### Step 1: Create `.streamlit/secrets.toml` File

Create a new file in your project:
```bash
mkdir -p .streamlit
touch .streamlit/secrets.toml
```

Add your secrets to `.streamlit/secrets.toml`:
```toml
# OpenRouter API Configuration
OPENROUTER_API_KEY = "your-openrouter-api-key-here"
OPENROUTER_MODEL = "anthropic/claude-3.5-haiku"

# LangSmith Configuration (Optional)
LANGCHAIN_TRACING_V2 = "true"
LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com"
LANGCHAIN_API_KEY = "your-langsmith-api-key-here"
LANGCHAIN_PROJECT = "nlp-to-sql-app"

# Cache Configuration
CACHE_ENABLED = "true"
CACHE_TTL_SECONDS = "86400"
CACHE_MAX_SIZE_MB = "500"
CACHE_MAX_RESULT_SIZE_MB = "10"

# Company Configuration
COMPANY_NAME = "EMB Global"
```

### Step 2: Update `.gitignore`

Ensure these files are **NEVER** committed to Git:

```bash
# Add to .gitignore
.env
.streamlit/secrets.toml
database/*.db
__pycache__/
*.pyc
*.pyo
*.log
.DS_Store
```

### Step 3: Verify `.gitignore` is Working

```bash
# Check that secrets are not tracked
git status

# Should NOT see:
# - .env
# - .streamlit/secrets.toml
# - database/query_cache.db
```

---

## 🚀 Deployment to Streamlit Community Cloud

### Prerequisites
1. GitHub account
2. Streamlit Community Cloud account (free at https://streamlit.io/cloud)
3. Your code pushed to a GitHub repository

### Step-by-Step Deployment

#### 1. Push Code to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Add NLP to SQL application with caching"

# Create GitHub repository (go to github.com and create new repo)
# Then push your code
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

**IMPORTANT**: Verify `.env` and `secrets.toml` are NOT in your GitHub repository!

#### 2. Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Connect your GitHub account
4. Select your repository and branch (main)
5. Set main file path: `app.py`
6. Click "Advanced settings"

#### 3. Configure Secrets in Streamlit Cloud

In the "Secrets" section, paste the contents of your `.streamlit/secrets.toml`:

```toml
OPENROUTER_API_KEY = "your-openrouter-api-key-here"
OPENROUTER_MODEL = "anthropic/claude-3.5-haiku"
LANGCHAIN_TRACING_V2 = "true"
LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com"
LANGCHAIN_API_KEY = "your-langsmith-api-key-here"
LANGCHAIN_PROJECT = "nlp-to-sql-app"
CACHE_ENABLED = "true"
CACHE_TTL_SECONDS = "86400"
CACHE_MAX_SIZE_MB = "500"
CACHE_MAX_RESULT_SIZE_MB = "10"
COMPANY_NAME = "EMB Global"
```

#### 4. Click "Deploy"!

Your app will be live at: `https://YOUR_USERNAME-YOUR_REPO_NAME.streamlit.app`

---

## 🔒 Security Best Practices

### ✅ DO:
- ✅ Use Streamlit secrets for all API keys
- ✅ Add `.env` and `secrets.toml` to `.gitignore`
- ✅ Use environment variables (`os.getenv()`)
- ✅ Regularly rotate API keys
- ✅ Monitor API usage on OpenRouter dashboard
- ✅ Set spending limits on OpenRouter account

### ❌ DON'T:
- ❌ NEVER commit `.env` files to Git
- ❌ NEVER hardcode API keys in source code
- ❌ NEVER share secrets in screenshots or documentation
- ❌ NEVER push `secrets.toml` to GitHub
- ❌ NEVER log API keys (even partially)

---

## 📋 Requirements File

Ensure `requirements.txt` is up to date for Streamlit Cloud:

```txt
streamlit>=1.28.0
pandas>=2.0.0
langchain>=1.2.0
langchain-openai>=1.1.8
langchain-community>=0.4.0
langchain-experimental>=0.4.0
langchain-core>=1.2.0
plotly>=5.14.0
openpyxl>=3.1.0
python-dotenv>=1.0.0
reportlab>=4.0.0
sqlalchemy>=2.0.0
```

---

## 🗄️ Database Considerations

### SQLite Limitations on Streamlit Cloud

Streamlit Cloud has an **ephemeral file system**, meaning:
- Files written during runtime are lost on reboot
- Cache database will reset periodically

### Solution Options:

#### Option 1: Accept Ephemeral Cache (Simple)
- Cache works during session
- Resets on app restart (every ~3-7 days)
- **Recommended for development/demo**

#### Option 2: External Database (Production)
Use a persistent database for caching:

**PostgreSQL (Recommended)**:
```python
# Update config.py
CACHE_DB_URL = os.getenv("CACHE_DATABASE_URL", "postgresql://...")

# Use SQLAlchemy instead of sqlite3
from sqlalchemy import create_engine
```

**Free PostgreSQL Providers**:
- Supabase (https://supabase.com) - 500MB free
- Neon (https://neon.tech) - 3GB free
- ElephantSQL (https://www.elephantsql.com) - 20MB free

#### Option 3: Redis (Advanced)
For high-performance caching:
- Upstash Redis (https://upstash.com) - 10k requests/day free
- Requires modifying `cache_manager.py`

---

## 🔧 Configuration for Production

### Adjust Cache Settings for Streamlit Cloud

Update `.streamlit/secrets.toml`:

```toml
# Reduce cache size for free tier
CACHE_MAX_SIZE_MB = "100"  # Reduced from 500MB
CACHE_TTL_SECONDS = "3600"  # 1 hour instead of 24h
```

### Monitor Usage

Add logging to track cache effectiveness:

```python
# Check logs in Streamlit Cloud dashboard
logger.info(f"Cache stats: {cache_manager.get_statistics()}")
```

---

## 🧪 Testing Before Deployment

### Local Testing with Secrets

1. Test with `secrets.toml`:
```bash
# Your app should read from st.secrets in production
streamlit run app.py
```

2. Update `config.py` to support both `.env` and `st.secrets`:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (local development)
load_dotenv()

# Try Streamlit secrets first (production), fallback to env vars (local)
try:
    import streamlit as st
    OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))
    OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku"))
    # ... repeat for other secrets
except:
    # Fallback to environment variables
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")
    # ... other configs
```

### Pre-Deployment Checklist

- [ ] `.env` is in `.gitignore`
- [ ] `secrets.toml` is in `.gitignore`
- [ ] No hardcoded API keys in code
- [ ] `requirements.txt` is complete
- [ ] Local testing passes with secrets
- [ ] Confirmed `.env` NOT in GitHub repo
- [ ] Prepared secrets for Streamlit Cloud dashboard

---

## 📊 Monitoring After Deployment

### Check Application Health

1. **Streamlit Cloud Dashboard**:
   - View app logs
   - Check resource usage
   - Monitor errors

2. **OpenRouter Dashboard**:
   - Track API usage
   - Monitor costs
   - Set spending alerts

3. **Application Logs**:
```bash
# In Streamlit Cloud, check logs for:
# - "Cache HIT" messages (caching working)
# - "Cache MISS" messages (new queries)
# - API errors (authentication issues)
```

---

## 🆘 Troubleshooting

### Issue: "OpenRouter API key not found"
**Solution**: Check secrets are properly set in Streamlit Cloud dashboard

### Issue: Cache not persisting
**Solution**: Expected behavior on Streamlit Cloud - see "Database Considerations"

### Issue: "ModuleNotFoundError"
**Solution**: Update `requirements.txt` with missing package

### Issue: App crashes on startup
**Solution**: Check logs in Streamlit Cloud dashboard for specific error

---

## 📞 Support Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **Streamlit Community**: https://discuss.streamlit.io/
- **OpenRouter Docs**: https://openrouter.ai/docs
- **GitHub Issues**: Create issues in your repository

---

## 🎯 Quick Deployment Summary

```bash
# 1. Ensure secrets are not in Git
git status  # Verify .env, secrets.toml not listed

# 2. Push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main

# 3. Deploy on Streamlit Cloud
# - Go to https://share.streamlit.io/
# - Connect GitHub repo
# - Add secrets in dashboard
# - Click Deploy

# 4. Verify deployment
# - Test queries work
# - Check caching (should see ⚡ on repeated queries)
# - Monitor OpenRouter usage
```

---

## ✅ Post-Deployment

Your application is now:
- ✅ Securely deployed
- ✅ API keys protected
- ✅ Caching enabled
- ✅ Accessible via public URL
- ✅ Free to use (within Streamlit Cloud limits)

**Share your app URL**: `https://YOUR_USERNAME-YOUR_REPO_NAME.streamlit.app`

Enjoy your deployed NLP to SQL application! 🎉
