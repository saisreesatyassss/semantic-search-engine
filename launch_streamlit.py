import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run streamlit
from streamlit import cli

if __name__ == "__main__":
    cli.main(['run', 'web_app/app.py', '--server.port=8501', '--server.address=0.0.0.0'])
