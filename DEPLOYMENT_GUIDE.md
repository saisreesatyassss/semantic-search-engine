# 🚀 Deploy to Streamlit Community Cloud

## Step-by-Step Deployment Guide

### Prerequisites
- GitHub account (free)
- Your code committed to GitHub

---

## 📤 DEPLOYMENT STEPS

### **Step 1: Push to GitHub**

```bash
# Create a new repository on GitHub (don't initialize it)
# Then push your code:

git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch-M main
git push -u origin main
```

**Or if you already have a repo:**
```bash
git push origin main
```

---

### **Step 2: Go to Streamlit Community Cloud**

1. Visit: **https://streamlit.io/cloud**
2. Click **"Get started free"** or **"Deploy"** button
3. Sign in with your **GitHub account**

---

### **Step 3: Connect Your Repository**

1. Click **"New app"**
2. Select your repository from the list
3. Choose branch: **main**
4. Set file path: **`web_app/app.py`**

---

### **Step 4: Configure Settings**

**App Settings:**
- **App title**: Semantic Search Engine
- **File path**: `web_app/app.py`
- **Branch**: main
- **Python version**: 3.8 or higher

**Advanced Settings (if needed):**
```
PYTHONPATH = .
```

---

### **Step 5: Deploy!**

1. Click **"Deploy!"** button
2. Wait 2-5 minutes for first deployment
3. Your app will be live at: `https://your-username-yourrepo-app-abc123.streamlit.app`

---

## ⚙️ REQUIRED FILES FOR DEPLOYMENT

Your repository must include:

✅ `web_app/app.py` - Main Streamlit app  
✅ `requirements.txt` - Python dependencies  
✅ `search_engine/` - Search engine module  
✅ `vector_database/` - FAISS index files  
✅ `data/` - Metadata files  
✅ `config.yaml` - Configuration  

---

## 📦 CREATE REQUIREMENTS.TXT

If not already present, create `requirements.txt`:

```txt
streamlit==1.28.0
sentence-transformers==2.2.2
faiss-cpu==1.7.4
numpy==1.24.3
pandas==2.0.3
PyYAML==6.0.1
scikit-learn==1.3.0
torch==2.0.1
```

---

## 🔧 TROUBLESHOOTING

### App won't deploy?

**1. Check File Paths**
- Ensure `web_app/app.py` exists
- Verify all imports are correct

**2. Missing Dependencies**
- Add all required packages to `requirements.txt`
- Include version numbers for stability

**3. Large Files**
- FAISS index might be large (>100MB)
- Consider using Git LFS for large files:
```bash
git lfs install
git lfs track "*.index"
git add .
git commit -m "Track large files with LFS"
git push
```

**4. Import Errors**
- Make sure all modules are in the repository
- Check relative import paths

---

## 🌐 YOUR DEPLOYED APP WILL HAVE:

✅ **Free hosting** - No credit card required  
✅ **Automatic HTTPS** - Secure by default  
✅ **Continuous deployment** - Auto-deploy on git push  
✅ **Public URL** - Share with anyone  
✅ **Community features** - Explore other apps  

---

## 📊 AFTER DEPLOYMENT

### Share Your App

Once deployed, you'll get a URL like:
```
https://yourusername-semanticsearchapp-abc123.streamlit.app
```

Share it with:
- Friends and colleagues
- Social media
- Portfolio
- Resume/CV

---

## 🔄 UPDATING YOUR APP

After initial deployment:

```bash
# Make changes locally
git add .
git commit -m "Update feature X"
git push origin main
```

Streamlit Cloud will **automatically redeploy** in 2-3 minutes!

---

## 💡 PRO TIPS

1. **Keep FAISS index under 100MB** for faster deployments
2. **Use environment variables** for sensitive data
3. **Add a `.streamlit/config.toml`** for custom settings
4. **Monitor deployment logs** in Streamlit Cloud dashboard
5. **Pin dependency versions** in requirements.txt for stability

---

## 🎯 EXAMPLE DEPLOYMENT CHECKLIST

- [ ] Code pushed to GitHub
- [ ] `requirements.txt` created
- [ ] All necessary files included
- [ ] Large files tracked with Git LFS (if needed)
- [ ] Signed in to Streamlit Cloud
- [ ] Repository connected
- [ ] File path set to `web_app/app.py`
- [ ] Deploy button clicked
- [ ] App successfully deployed!

---

## 🆘 NEED HELP?

- **Streamlit Docs**: https://docs.streamlit.io
- **Community Forum**: https://discuss.streamlit.io
- **GitHub Issues**: Report bugs in your repo

---

## 🎉 CONGRATULATIONS!

Your Semantic Search Engine is now live on Streamlit Community Cloud!

**Features:**
- ✅ Free forever
- ✅ Public access
- ✅ Automatic updates
- ✅ Professional portfolio piece

**Next Steps:**
1. Test your deployed app
2. Share the URL
3. Monitor usage in Streamlit dashboard
4. Keep building amazing features!

---

**Happy Deploying! 🚀**
