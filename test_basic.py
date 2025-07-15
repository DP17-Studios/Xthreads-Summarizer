#!/usr/bin/env python3
"""
Basic test script to verify the application components work correctly
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """
    Test if all required modules can be imported
    """
    print("Testing imports...")
    
    try:
        import fastapi
        print("FastAPI imported successfully")
    except ImportError as e:
        print(f"FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("Uvicorn imported successfully")
    except ImportError as e:
        print(f"Uvicorn import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("python-dotenv imported successfully")
    except ImportError as e:
        print(f"python-dotenv import failed: {e}")
        return False
    
    return True

def test_firecrawl_module():
    """
    Test the firecrawl module functionality
    """
    print("\nTesting firecrawl module...")
    
    try:
        from xthread_scraper import ThreadScraper
        print("ThreadScraper class imported successfully")
        
        # Test URL validation without API call
        scraper = ThreadScraper.__new__(ThreadScraper)  # Create without __init__
        
        # Test URL validation method
        valid_urls = [
            "https://twitter.com/user/status/1234567890",
            "https://x.com/user/status/1234567890",
            "https://www.twitter.com/user/status/1234567890"
        ]
        
        invalid_urls = [
            "https://facebook.com/user/post/123",
            "https://twitter.com/user",
            "not_a_url",
            ""
        ]
        
        for url in valid_urls:
            if scraper._validate_twitter_url(url):
                print(f"Valid URL correctly identified: {url}")
            else:
                print(f"Invalid URL incorrectly rejected: {url}")
                return False
        
        for url in invalid_urls:
            if not scraper._validate_twitter_url(url):
                print(f"Invalid URL correctly rejected: {url}")
            else:
                print(f"Invalid URL incorrectly accepted: {url}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Firecrawl module test failed: {e}")
        return False

def test_summarizer_module():
    """
    Test the summarizer module functionality
    """
    print("\nTesting summarizer module...")
    
    try:
        from summarizer import ThreadSummarizer, MultiProviderSummarizer
        print("Summarizer classes imported successfully")
        
        # Test bullet point extraction without LLM
        summarizer = ThreadSummarizer.__new__(ThreadSummarizer)
        
        test_summary = """
        • First bullet point about something important
        • Second bullet point with more details
        • Third bullet point explaining concepts
        • Fourth bullet point with actionable insights
        • Fifth bullet point summarizing key takeaways
        """
        
        bullet_points = summarizer._extract_bullet_points(test_summary)
        
        if len(bullet_points) == 5:
            print("Bullet point extraction working correctly")
            for i, point in enumerate(bullet_points, 1):
                print(f"  {i}. {point[:50]}...")
        else:
            print(f"Expected 5 bullet points, got {len(bullet_points)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Summarizer module test failed: {e}")
        return False

def test_main_module():
    """
    Test the main FastAPI module
    """
    print("\nTesting main module...")
    
    try:
        from main import app
        print("FastAPI app imported successfully")
        
        # Check if required routes exist
        routes = [route.path for route in app.routes]
        
        required_routes = ["/", "/health", "/api/summarize", "/summarize"]
        
        for route in required_routes:
            if route in routes:
                print(f"Route {route} exists")
            else:
                print(f"Route {route} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Main module test failed: {e}")
        return False

def test_file_structure():
    """
    Test if all required files exist
    """
    print("\nTesting file structure...")
    
    required_files = [
        "main.py",
        "xthread_scraper.py",
        "summarizer.py",
        "requirements.txt",
        "templates/index.html",
        "static/style.css",
        ".env.example",
        "README.md"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"{file_path} exists")
        else:
            print(f"{file_path} missing")
            return False
    
    return True

def main():
    """
    Run all tests
    """
    print("=" * 50)
    print("Twitter Thread Summarizer - Basic Tests")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_imports,
        test_firecrawl_module,
        test_summarizer_module,
        test_main_module
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"Test {test_func.__name__} failed")
        except Exception as e:
            print(f"Test {test_func.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! The application is ready to use.")
        print("\nNext steps:")
        print("1. Create a .env file with your API keys")
        print("2. Run: python main.py")
        print("3. Visit: http://localhost:8000")
        return True
    else:
        print("Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
