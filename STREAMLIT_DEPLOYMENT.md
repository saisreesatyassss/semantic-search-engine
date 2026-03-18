# Streamlit Community Cloud Deployment Guide

## ✅ Project Status: Ready for Deployment

This project is configured for deployment on Streamlit Community Cloud.

## 📋 Deployment Checklist

### 1. Entry File ✓
- **Main file**: `app.py` (created)
- **Entry point**: Streamlit app that imports from `web_app/app.py`

### 2. Requirements ✓
- **File**: `requirements.txt`
- Uses `faiss-cpu` (not faiss-gpu)
- Includes all necessary packages
- Removed test dependencies to reduce build time

### 3. Model Caching ✓
- BERT model loading uses `@st.cache_resource`
- Prevents reloading on every interaction

### 4. Configuration ✓
- `.streamlit/config.toml` configured
- Port: 8501
- Headless mode enabled

## 🚀 Deployment Steps

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New App"**
3. Select your repository
4. Configure:
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click **"Deploy!"**

## ⚙️ Repository Structure

```
semantic-search-engine/
├── app.py                 # Main entry point for Streamlit Cloud
├── requirements.txt       # Dependencies
├── config.yaml           # Configuration
├── web_app/
│   └── app.py            # Streamlit application logic
├── search_engine/
│   └── semantic_search.py # Search functionality
├── embeddings/
│   └── embedding_generator.py
├── vector_database/
│   └── faiss_index.py
├── data/
│   └── processed/        # Pre-built index and embeddings
└── models/               # Cached models
```

## 🔧 Important Notes

### Model Download
- First deployment will take longer (downloads BERT model ~500MB)
- Subsequent loads use caching
- Model: `all-MiniLM-L6-v2`

### FAISS Index
- Pre-built index in `vector_database/faiss.index`
- Size: Check before deploying (should be <100MB ideally)
- If too large, consider rebuilding with fewer documents

### Memory Limits
- Streamlit Cloud: ~1GB RAM
- Current setup optimized for CPU usage
- Large indices may cause memory issues

## 🐛 Troubleshooting

### Build Fails
- Check `requirements.txt` formatting
- Ensure no typos in package names
- Build time limit: 15 minutes

### Runtime Errors
- Missing data files: Ensure `data/processed/` contains required files
- Model download fails: Check internet connectivity
- Memory error: Reduce dataset size or FAISS index

### App Won't Load
- Verify `app.py` exists at root
- Check import paths in code
- Review logs in Streamlit dashboard

## 📊 Performance Optimization

The app includes:
- ✅ Model caching with `@st.cache_resource`
- ✅ Efficient FAISS indexing
- ✅ Minimal UI for fast loading
- ✅ Optimized data loading

## 🎯 Next Steps After Deployment

1. Test the deployed app with sample queries
2. Monitor performance in Streamlit dashboard
3. Check memory usage
4. Verify search results quality

## 📞 Support

If you encounter issues:
1. Check Streamlit Cloud logs
2. Review deployment guide
3. Test locally first: `streamlit run app.py`
4. Compare with local environment
