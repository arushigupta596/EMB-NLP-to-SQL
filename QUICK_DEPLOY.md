# Quick Deployment Guide - TL;DR

## 🚀 Deploy to Streamlit Cloud in 5 Minutes

### Step 1: Push to GitHub (30 seconds)
```bash
cd "/Users/arushigupta/Desktop/EMB/Demos/NLP to SQL"
git add .
git commit -m "Deploy NLP to SQL app"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud (2 minutes)
1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your GitHub repo → `main` branch → `app.py`
4. Click "Advanced settings"
5. Paste this in "Secrets" section:

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

6. Click "Deploy"

### Step 3: Done! (2 minutes)
Your app will be live at: `https://YOUR_USERNAME-YOUR_REPO.streamlit.app`

---

## ✅ Pre-Deployment Checklist
- [x] `.env` in `.gitignore` ✓
- [x] `secrets.toml` in `.gitignore` ✓
- [x] Cache management UI removed ✓
- [x] No hardcoded API keys ✓
- [x] Ready to deploy! 🎉

---

## 🔒 Security Notes
- ✅ API keys stored in Streamlit Cloud secrets (encrypted)
- ✅ Never committed to Git
- ✅ Cache works but resets on app restart (ephemeral storage)
- ✅ Safe to share app URL publicly

---

## 🆘 If Something Goes Wrong

**Can't find secrets in Streamlit Cloud?**
- Settings → Secrets → Paste the config above

**App not starting?**
- Check logs in Streamlit Cloud dashboard
- Verify all secrets are set

**API key error?**
- Double-check OpenRouter key is correct
- Visit https://openrouter.ai/keys to verify

---

**That's it! Your app is deployed securely. 🚀**
