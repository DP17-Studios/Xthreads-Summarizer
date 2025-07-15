#!/usr/bin/env python3
"""
Dependency installer script that handles package installation gracefully
"""

import subprocess
import sys

def install_package(package):
    """
    Install a single package using pip
    """
    try:
        print(f"Installing {package}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"[OK] {package} installed successfully")
            return True
        else:
            print(f"[FAIL] {package} installation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {package} installation timed out")
        return False
    except Exception as e:
        print(f"[ERROR] {package} installation error: {e}")
        return False

def main():
    """
    Install all required packages
    """
    print("Installing Twitter Thread Summarizer dependencies...")
    print("=" * 50)
    
    # Core packages first
    core_packages = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "python-multipart==0.0.6",
        "jinja2==3.1.2",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "aiofiles==23.2.1",
        "pydantic==2.5.0"
    ]
    
    # LangChain packages
    langchain_packages = [
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "langchain-openai>=0.0.2",
        "langchain-mistralai>=0.0.1"
    ]
    
    # Firecrawl package
    firecrawl_packages = [
        "firecrawl-py>=0.0.16"
    ]
    
    all_packages = core_packages + langchain_packages + firecrawl_packages
    
    installed = 0
    total = len(all_packages)
    
    for package in all_packages:
        if install_package(package):
            installed += 1
        else:
            print(f"Skipping {package} due to installation failure")
    
    print("\n" + "=" * 50)
    print(f"Installation complete: {installed}/{total} packages installed")
    
    if installed == total:
        print("SUCCESS: All dependencies installed successfully!")
        return True
    else:
        print(f"WARNING: {total - installed} packages failed to install")
        print("The application may not work correctly.")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\nNext steps:")
        print("1. Create a .env file with your API keys")
        print("2. Run: python main.py")
        print("3. Visit: http://localhost:8000")
    else:
        print("\nSome packages failed to install. You may need to:")
        print("1. Update pip: python -m pip install --upgrade pip")
        print("2. Install packages manually")
        print("3. Check your internet connection")
    
    sys.exit(0 if success else 1)
