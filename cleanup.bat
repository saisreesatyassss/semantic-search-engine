@echo off
REM Cleanup script to remove unnecessary files before deployment

echo ============================================================
echo CLEANING UP UNNECESSARY FILES FOR STREAMLIT DEPLOYMENT
echo ============================================================
echo.

echo [1/5] Removing .git folder...
if exist ".git" (
    rmdir /s /q ".git"
    echo Removed .git folder
) else (
    echo .git folder not found (already clean)
)
echo.

echo [2/5] Removing .qoder folder...
if exist ".qoder" (
    rmdir /s /q ".qoder"
    echo Removed .qoder folder
) else (
    echo .qoder folder not found (already clean)
)
echo.

echo [3/5] Removing __pycache__ folders...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo Removed all __pycache__ folders
echo.

echo [4/5] Removing Python cache files...
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
echo Removed Python cache files
echo.

echo [5/5] Removing temporary files...
del /s /q *.tmp 2>nul
del /s /q *.log 2>nul
echo Removed temporary files
echo.

echo ============================================================
echo CLEANUP COMPLETE!
echo ============================================================
echo.
echo Your project is now clean and ready for Streamlit deployment.
echo.
echo Next steps:
echo 1. git add .
echo 2. git commit -m "Clean up for Streamlit deployment"
echo 3. git push origin main
echo 4. Deploy at share.streamlit.io
echo.
pause
