@echo off
REM Quick Deployment Script for Streamlit Cloud
REM This script prepares your project for deployment

echo ============================================
echo Semantic Search Engine - Deployment Prep
echo ============================================
echo.

REM Step 1: Check if git is initialized
if not exist ".git" (
    echo [1/4] Initializing Git repository...
    git init
) else (
    echo [1/4] Git repository already exists
)

REM Step 2: Add all files
echo [2/4] Adding all files to git...
git add .

REM Step 3: Commit changes
echo [3/4] Committing changes...
git commit -m "Ready for Streamlit Cloud deployment"

REM Step 4: Show next steps
echo.
echo ============================================
echo Preparation Complete!
echo ============================================
echo.
echo NEXT STEPS:
echo.
echo 1. Create a GitHub repository:
echo    - Go to https://github.com/new
echo    - Repository name: semantic-search-engine
echo    - Keep it Public (required for free tier)
echo    - Click "Create repository"
echo.
echo 2. Connect and push to GitHub:
echo    git remote add origin https://github.com/YOUR_USERNAME/semantic-search-engine.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. Deploy on Streamlit Cloud:
echo    - Go to https://share.streamlit.io
echo    - Sign in with GitHub
echo    - Click "New app"
echo    - Select your repository
echo    - Set Main file path to: web_app/app_cloud.py
echo    - Click "Deploy!"
echo.
echo 4. Wait 5-10 minutes for deployment
echo.
echo Your app will be live at:
echo https://YOUR_USERNAME-semantic-search-engine.streamlit.app
echo.
echo ============================================
echo For detailed instructions, see:
echo DEPLOYMENT_GUIDE.md
echo ============================================
echo.
pause
