#!/usr/bin/env python3
"""
Deployment helper script for Smart Chatbot Kota Cimahi
This script helps prepare the application for deployment to Streamlit Cloud
"""

import os
import shutil
import sys
from pathlib import Path

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        "app4.py",
        "requirements.txt", 
        ".streamlit/config.toml",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present")
        return True

def check_optional_files():
    """Check optional FAISS files"""
    optional_files = [
        "extracted/faiss_index",
        "extracted/faiss_metadata.json", 
        "extracted/chunks.json"
    ]
    
    present_files = []
    missing_files = []
    
    for file in optional_files:
        if os.path.exists(file):
            present_files.append(file)
        else:
            missing_files.append(file)
    
    if present_files:
        print("✅ FAISS files found:")
        for file in present_files:
            print(f"   - {file}")
    
    if missing_files:
        print("⚠️  Missing FAISS files (app will work with limited functionality):")
        for file in missing_files:
            print(f"   - {file}")

def create_deployment_checklist():
    """Create a deployment checklist"""
    checklist = """
# 🚀 Deployment Checklist for Streamlit Cloud

## Pre-deployment
- [ ] All required files present (app4.py, requirements.txt, config.toml)
- [ ] Code pushed to GitHub repository
- [ ] API keys ready (OpenRouter, Jina AI)
- [ ] FAISS files included (optional)

## Streamlit Cloud Setup
1. [ ] Go to https://share.streamlit.io
2. [ ] Connect GitHub account
3. [ ] Click "New app"
4. [ ] Select repository
5. [ ] Set main file: app4.py
6. [ ] Click "Deploy!"

## Configure Secrets
Add these secrets in Streamlit Cloud dashboard:
```
OPENROUTER_API_KEY = "your_key_here"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "deepseek/deepseek-r1-0528:free"
JINA_API_KEY = "your_key_here"
```

## Post-deployment
- [ ] Test all features (chatbot, complaints, admin)
- [ ] Verify FAISS functionality
- [ ] Check performance and error handling
- [ ] Monitor logs for issues

## Troubleshooting
- Check Streamlit Cloud logs if deployment fails
- Verify API keys are correct
- Ensure requirements.txt has all dependencies
- Check file paths are relative, not absolute
"""
    
    with open("DEPLOYMENT_CHECKLIST.md", "w", encoding="utf-8") as f:
        f.write(checklist)
    
    print("✅ Created DEPLOYMENT_CHECKLIST.md")

def main():
    print("🔧 Smart Chatbot Deployment Helper")
    print("=" * 40)
    
    # Check current directory
    if not os.path.exists("app4.py"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please ensure all required files are present before deployment")
        sys.exit(1)
    
    print()
    check_optional_files()
    
    print()
    create_deployment_checklist()
    
    print("\n🎉 Ready for deployment!")
    print("\nNext steps:")
    print("1. Push code to GitHub")
    print("2. Go to https://share.streamlit.io")
    print("3. Follow the deployment checklist")
    print("4. Add your API keys in secrets")

if __name__ == "__main__":
    main()
