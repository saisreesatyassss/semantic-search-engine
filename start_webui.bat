@echo off
REM Start Streamlit Web Interface
cd /d "%~dp0"
echo Starting Streamlit Web Interface...
echo.
echo Access the web interface at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.
python -c "import sys, os; os.system('python -m streamlit run web_app/app.py --server.port 8501 --server.headless true')"
pause
