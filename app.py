"""
Streamlit app.py - Main entry point for Streamlit Community Cloud deployment
This file integrates all components for the Semantic Search Engine
"""
import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function from the web_app module
from web_app.app import main as web_app_main

def main():
    """Main entry point that calls the web application."""
    # Run the main web application
    web_app_main()

if __name__ == "__main__":
    main()
