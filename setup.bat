@echo off
REM Complete setup and run script for Semantic Search Engine (Windows)
REM This script automates the entire setup process

echo ==========================================
echo Semantic Search Engine Setup Script
echo ==========================================
echo.

REM Step 1: Check Python version
echo [1/6] Checking Python version...
python --version
echo.

REM Step 2: Create virtual environment if it doesn't exist
echo [2/6] Setting up virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
) else (
    echo Virtual environment already exists
)
echo.

REM Step 3: Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo Environment activated
echo.

REM Step 4: Install dependencies
echo [4/6] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Dependencies installed
echo.

REM Step 5: Download NLTK data
echo [5/6] Downloading NLTK data...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
echo NLTK data downloaded
echo.

REM Step 6: Run data pipeline
echo [6/6] Running data preparation pipeline...
echo.
echo Running download_data.py...
python scripts\download_data.py

echo.
echo Running build_index.py...
python scripts\build_index.py

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Start the API server:
echo    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 2. In a new terminal, start the web UI:
echo    streamlit run web_app\app.py --server.port 8501
echo.
echo 3. Access the services:
echo    - API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo    - Web UI: http://localhost:8501
echo.
echo For more information, see README.md or QUICKSTART.md
echo.
pause
