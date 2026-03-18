#!/bin/bash
# Complete setup and run script for Semantic Search Engine
# This script automates the entire setup process

set -e  # Exit on error

echo "=========================================="
echo "Semantic Search Engine Setup Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Python version
echo -e "${YELLOW}[1/6] Checking Python version...${NC}"
python_version=$(python --version 2>&1)
echo "Found: $python_version"

# Step 2: Create virtual environment if it doesn't exist
echo -e "${YELLOW}[2/6] Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Step 3: Activate virtual environment
echo -e "${YELLOW}[3/6] Activating virtual environment...${NC}"
source venv/bin/activate  # For Linux/Mac
# For Windows, use: venv\Scripts\activate
echo -e "${GREEN}✓ Environment activated${NC}"

# Step 4: Install dependencies
echo -e "${YELLOW}[4/6] Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 5: Download NLTK data
echo -e "${YELLOW}[5/6] Downloading NLTK data...${NC}"
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
echo -e "${GREEN}✓ NLTK data downloaded${NC}"

# Step 6: Run data pipeline
echo -e "${YELLOW}[6/6] Running data preparation pipeline...${NC}"
echo ""
echo "Running download_data.py..."
python scripts/download_data.py

echo ""
echo "Running build_index.py..."
python scripts/build_index.py

echo ""
echo -e "${GREEN}=========================================="
echo "Setup Complete! 🎉"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Start the API server:"
echo "   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. In a new terminal, start the web UI:"
echo "   streamlit run web_app/app.py --server.port 8501"
echo ""
echo "3. Access the services:"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Web UI: http://localhost:8501"
echo ""
echo "For more information, see README.md or QUICKSTART.md"
echo ""
