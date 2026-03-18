@echo off
REM Quick deployment script for Streamlit Community Cloud

echo ============================================================
echo STREAMLIT CLOUD DEPLOYMENT SCRIPT
echo ============================================================
echo.

REM Step 1: Run pre-deployment tests
echo [Step 1/4] Running pre-deployment tests...
python test_deployment.py
if errorlevel 1 (
    echo.
    echo ERROR: Pre-deployment tests failed!
    echo Please fix the issues before deploying.
    pause
    exit /b 1
)
echo.

REM Step 2: Check Git status
echo [Step 2/4] Checking Git repository...
git status >nul 2>&1
if errorlevel 1 (
    echo ERROR: Not a Git repository!
    echo.
    echo Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit"
)
echo.

REM Step 3: Commit and push changes
echo [Step 3/4] Committing and pushing to Git...
git add .
git commit -m "Deploy to Streamlit Cloud - %DATE% %TIME%"
if errorlevel 1 (
    echo WARNING: Git commit failed. Please commit manually.
) else (
    echo Git commit successful!
    echo.
    echo Pushing to remote repository...
    git push origin main
    if errorlevel 1 (
        echo WARNING: Git push failed. Please push manually.
        echo Make sure you have a remote repository configured.
    ) else (
        echo Git push successful!
    )
)
echo.

REM Step 4: Display deployment instructions
echo [Step 4/4] Deployment Instructions
echo ============================================================
echo.
echo Your code has been pushed to GitHub!
echo.
echo NEXT STEPS:
echo 1. Go to https://share.streamlit.io
echo 2. Login with your GitHub account
echo 3. Click "New App"
echo 4. Configure your app:
echo    -Repository: YOUR_REPO_NAME
echo    - Branch: main
echo    - Main file path: app.py
echo 5. Click "Deploy!"
echo.
echo First deployment will take 5-10 minutes (downloading BERT model)
echo.
echo Monitor the deployment in the Streamlit dashboard.
echo ============================================================
echo.
pause
