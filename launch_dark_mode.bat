@echo off
REM Launch Semantic Search Engine with Dark Mode
echo ============================================
echo Semantic Search Engine - Dark Mode Edition
echo ============================================
echo.
echo Features:
echo - Toggle between Dark and Light mode
echo - Professional design
echo - Smooth theme transitions
echo.
echo Access at: http://localhost:8501
echo.
python -m streamlit run web_app/app_with_dark_mode.py --server.port 8501 --server.address 0.0.0.0
pause
