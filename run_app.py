#!/usr/bin/env python3
"""
Startup script for Nano Banana Streamlit app
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import streamlit
        from google import genai
        from PIL import Image
        from dotenv import load_dotenv
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_api_key():
    """Check if API key is configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        print("❌ API key not configured")
        print("Please add your Google AI API key to the .env file")
        print("Get your API key from: https://aistudio.google.com/app/apikey")
        return False
    
    print("✅ API key configured")
    return True

def create_directories():
    """Create necessary directories"""
    dirs = ['generated_images', 'utils']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("✅ Directories ready")

def main():
    """Main startup function"""
    print("🍌 Starting Nano Banana...")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check API key
    if not check_api_key():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Start Streamlit
    print("🚀 Launching Streamlit app...")
    print("The app will open in your browser automatically")
    print("Press Ctrl+C to stop the app")
    print("=" * 40)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless=false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down Nano Banana...")

if __name__ == "__main__":
    main()