# Streamlit Community Cloud Deployment Checklist

## ✅ Pre-Deployment Verification

### 1. File Structure ✓
- [x] `app.py` exists at root (main entry point)
- [x] `requirements.txt` at root
- [x] `.streamlit/config.toml` configured
- [x] All Python modules in proper directories

### 2. Dependencies ✓
- [x] `faiss-cpu` instead of `faiss` (CPU-only deployment)
- [x] `streamlit` included
- [x] `sentence-transformers` included
- [x] Test dependencies removed (pytest, etc.)
- [x] `pyyaml` added for config loading

### 3. Model Caching ✓
- [x] `@st.cache_resource` decorator used in `web_app/app.py`
- [x] Model loading happens once per session
- [x] No redundant model reloading

### 4. Data Files Size ✓
- FAISS Index: **14.65 MB** ✓ (Under 100MB limit)
- Embeddings: **14.65 MB** ✓
- Metadata: **0.34 MB** ✓
- **Total Core Data: ~30 MB** ✓ (Well under 1GB repo limit)

### 5. Memory Optimization ✓
- Total project size: **~50 MB** (under 1GB limit)
- Expected RAM usage: **~500-800 MB** (under 1GB limit)
- CPU-based inference (no GPU required)

---

## 🚀 Deployment Steps

### Step 1: Local Testing
```bash
# Test the app locally before deploying
cd "semantic-search-engine"
streamlit run app.py
```

**Verify:**
- App loads without errors
- Search functionality works
- Results display correctly
- No console errors

### Step 2: Git Repository Setup

#### If not already using Git:
```bash
git init
git add .
git commit -m "Initial commit - Semantic Search Engine ready for Streamlit Cloud"
```

#### Add remote repository (GitHub):
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Streamlit Cloud

1. **Go to**: [https://share.streamlit.io](https://share.streamlit.io)

2. **Login** with your GitHub account

3. **Click "New App"**

4. **Configure:**
   - **Repository**: Select your repository
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **Advanced Settings** (optional):
     - Leave default

5. **Click "Deploy!"**

### Step 4: Monitor Deployment

- Watch the build logs in Streamlit dashboard
- First build will take **5-10 minutes** (downloading BERT model ~500MB)
- Subsequent loads will be faster due to caching

---

## ⚠️ Common Issues & Solutions

### Issue 1: Build Fails with "ModuleNotFoundError"
**Solution**: Check `requirements.txt` has all packages
```txt
streamlit
sentence-transformers
faiss-cpu
pandas
numpy
scikit-learn
pyyaml
```

### Issue 2: "Memory Error" During Build
**Cause**: Dataset or index too large  
**Solution**: 
- Current setup is optimized (~30MB data files)
- If you add more data, keep total under 100MB

### Issue 3: App Loads But Search Doesn't Work
**Check**:
1. FAISS index file exists: `vector_database/faiss.index`
2. Metadata file exists: `data/processed/metadata.pkl`
3. Paths are correct in imports

### Issue 4: Slow First Load
**Normal**: BERT model downloads on first request  
**Solution**: Wait 2-3 minutes for initial load, subsequent loads are fast

### Issue 5: "Build Timeout" (15 minutes)
**Solutions**:
- Reduce dataset size
- Use smaller model: `all-MiniLM-L6-v2` (already configured)
- Remove unnecessary dependencies from `requirements.txt`

---

## 📊 Performance Expectations

### Build Time
- **First build**: 5-10 minutes (model download)
- **Subsequent builds**: 2-5 minutes (cached dependencies)

### Runtime Performance
- **Cold start**: 30-60 seconds
- **Search latency**: 100-500ms per query
- **Memory usage**: ~500-800 MB

### Model Performance
- **Model**: `all-MiniLM-L6-v2`
- **Embedding dimension**: 384
- **Max sequence length**: 256 tokens
- **Inference**: CPU-optimized

---

## 🔍 Post-Deployment Verification

After deployment completes:

### 1. Test Basic Functionality
- [ ] App loads without errors
- [ ] Search bar appears
- [ ] Statistics show in sidebar
- [ ] Example queries visible

### 2. Test Search
- [ ] Enter a test query
- [ ] Results appear within 2 seconds
- [ ] Similarity scores display
- [ ] Result cards formatted correctly

### 3. Check Logs
- [ ] No ERROR messages in Streamlit logs
- [ ] No WARNING about missing files
- [ ] Model loads successfully

### 4. Performance Check
- [ ] Page loads in <10 seconds
- [ ] Search responds in <2 seconds
- [ ] No timeout errors

---

## 🎯 Optimization Tips

### For Better Performance:
1. **Use smaller datasets** if memory issues occur
2. **Enable caching** (already implemented)
3. **Reduce top_k results** if search is slow
4. **Consider hybrid search** for large datasets

### For Cost Savings:
1. **Sleep mode**: App sleeps after inactivity
2. **Wake-up time**: ~30 seconds on first visit
3. **No charges**: Free tier for Community Cloud

---

## 📞 Getting Help

### If Deployment Fails:
1. Check build logs in Streamlit dashboard
2. Review error messages
3. Compare with local environment
4. Test locally: `streamlit run app.py`

### Resources:
- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Community Forum**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **This Project's Guide**: `STREAMLIT_DEPLOYMENT.md`

---

## 🎉 Success Criteria

Your deployment is successful when:
- ✅ App loads without errors
- ✅ Search returns relevant results
- ✅ Response time <2 seconds
- ✅ No critical errors in logs
- ✅ Statistics show correct document count

---

## 📝 Maintenance

### To Update Your App:
```bash
# Make changes locally
git add .
git commit -m "Update description"
git push origin main
```

Streamlit Cloud will automatically redeploy (takes 2-5 minutes).

### To Force Redeploy:
1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Click "Settings"
4. Click "Redeploy"

---

**Last Updated**: March 10, 2026  
**Project Version**: 1.0.0  
**Status**: Ready for Deployment ✅
