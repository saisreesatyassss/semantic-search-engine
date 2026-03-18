# Streamlit Community Cloud Deployment Configuration

## 🚀 Deploy to Streamlit Community Cloud (FREE)

### Prerequisites
- GitHub account
- Your code pushed to a public GitHub repository

---

## 📋 Step-by-Step Deployment Guide

### **Step 1: Prepare Your Repository**

1. **Create a `.streamlit/secrets.toml` file** (for API configuration):
```toml
# Optional: Add any secrets or API keys here
# For now, no secrets needed as we're using local models
```

2. **Update `requirements.txt`** (already done - all dependencies listed)

3. **Create/update `setup.sh`** for Streamlit Cloud:
```bash
mkdir -p ~/.streamlit/
echo "[general]" > ~/.streamlit/credentials.toml
echo "email = \"your-email@example.com\"" >> ~/.streamlit/credentials.toml
```

### **Step 2: Push to GitHub**

```bash
# Initialize git repository (if not already done)
cd "c:\Users\Md Ameen\OneDrive\Desktop\Semantic Search\semantic-search-engine"
git init
git add .
git commit -m "Initial commit: Semantic Search Engine"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/semantic-search-engine.git
git branch -M main
git push -u origin main
```

### **Step 3: Deploy on Streamlit Cloud**

1. **Go to**: https://share.streamlit.io

2. **Sign in** with your GitHub account

3. **Click "New app"**

4. **Configure your app**:
   - **Repository**: Select your `semantic-search-engine` repo
   - **Branch**: `main`
   - **Main file path**: `web_app/app.py`
   - **Advanced Settings** → **Python Version**: `3.9` (or higher)

5. **Click "Deploy!"**

6. **Wait for deployment** (~5-10 minutes for first build)

7. **Your app URL**: `https://your-username-semantic-search-engine-abc123.streamlit.app`

---

## ⚠️ IMPORTANT: Data & Model Files

Streamlit Cloud has limitations:

### ❌ What WON'T Work:
- Local FAISS index files (need to be generated at runtime)
- Large cached embeddings (>200MB)
- Persistent storage between sessions

### ✅ What WILL Work:
- Pre-trained models (downloaded from HuggingFace)
- Small datasets (<200MB)
- Sample data for demo

---

## 🔧 MODIFIED DEPLOYMENT VERSION

Since Streamlit Cloud can't persist large files, I'll create a **deployment-ready version**:

### **Option 1: Use Smaller Dataset** (Recommended for Demo)

Create `web_app/app_deploy.py`:
- Downloads small sample dataset on startup
- Generates embeddings on-the-fly
- No persistent index needed
- Perfect for demos and learning

### **Option 2: Hybrid Approach**

Keep the full version but modify for cloud:
- Download pre-built index from cloud storage (Google Drive, S3)
- Or rebuild index at startup (takes ~2-3 minutes)
- Cache in session state

---

## 🎯 RECOMMENDED: Create Deployment Version

Let me create a Streamlit Cloud-compatible version:

**File: `web_app/app_cloud.py`**

This version will:
1. ✅ Use smaller sample dataset (1,000 docs instead of 10,000)
2. ✅ Generate embeddings on first load
3. ✅ Cache in memory for session
4. ✅ Work within Streamlit Cloud free tier limits
5. ✅ Still demonstrate full functionality

---

## 📊 Streamlit Cloud Free Tier Limits

| Resource | Limit | Our App Usage |
|----------|-------|---------------|
| **Storage** | Unlimited (ephemeral) | ✅ OK |
| **Memory** | 1GB RAM | ~500MB needed |
| **CPU** | Shared vCPU | ✅ OK for demo |
| **Data Transfer** | 50GB/month | ✅ OK for moderate use |
| **App Uptime** | Sleeps after 90 min idle | ⚠️ Wakes on demand |
| **Build Time** | 10 minutes max | ~5 minutes needed |

---

## 🚀 ALTERNATIVE: Deploy Full Version

For production use with full dataset, consider:

### **Snowflake Snowpark Container Services** (Enterprise)
- Private deployment
- Enterprise security
- Full data stack integration
- Cost: Pay for usage

### **Other Platforms** (Custom)
- **Heroku**: Easy deployment, $7-50/month
- **Railway**: Modern platform, $5-20/month
- **Render**: Simple hosting, free tier available
- **AWS/GCP/Azure**: Full control, pay-as-you-go

---

## 🎨 NEXT STEPS

Which deployment option would you like?

1. **Streamlit Cloud (Free)** - Public demo app with smaller dataset
2. **Docker + VPS** - Full private deployment ($5-10/month)
3. **Snowflake Enterprise** - Full enterprise features

Let me know and I'll prepare the deployment files! 🚀
