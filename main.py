from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl
import asyncio
import os
import logging
from dotenv import load_dotenv

# Import our custom modules
from xthread_scraper import ThreadScraper
from summarizer import MultiProviderSummarizer, ThreadSummarizer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Twitter Thread Summarizer",
    description="Extract and summarize Twitter/X threads using Firecrawl and LLM",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
try:
    thread_scraper = ThreadScraper()
    thread_summarizer = MultiProviderSummarizer(providers=["mistral", "openai"])
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    thread_scraper = None
    thread_summarizer = None

# Pydantic models
class ThreadRequest(BaseModel):
    url: str

class SummaryResponse(BaseModel):
    success: bool
    summary: dict = None
    error: str = None
    processing_time: float = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Serve the main HTML page
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "services": {
            "scraper": thread_scraper is not None,
            "summarizer": thread_summarizer is not None
        },
        "providers": thread_summarizer.providers if thread_summarizer else []
    }

@app.post("/api/summarize", response_model=SummaryResponse)
async def summarize_thread_api(request: ThreadRequest):
    """
    API endpoint to summarize a Twitter thread
    """
    import time
    start_time = time.time()
    
    try:
        # Validate services are available
        if not thread_scraper or not thread_summarizer:
            raise HTTPException(
                status_code=503,
                detail="Services not properly initialized. Check your API keys."
            )
        
        # Validate URL
        url = request.url.strip()
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        logger.info(f"Processing thread URL: {url}")
        
        # Step 1: Scrape the thread
        scrape_result = await thread_scraper.scrape_thread(url)
        
        if not scrape_result['success']:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to scrape thread: {scrape_result.get('error', 'Unknown error')}"
            )
        
        thread_data = scrape_result['thread_data']
        
        # Step 2: Summarize the content
        summary_result = await thread_summarizer.summarize_thread(thread_data)
        
        if not summary_result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate summary: {summary_result.get('error', 'Unknown error')}"
            )
        
        processing_time = time.time() - start_time
        
        return SummaryResponse(
            success=True,
            summary={
                "bullet_points": summary_result['summary']['bullet_points'],
                "author": summary_result['summary']['author'],
                "tweet_count": summary_result['summary']['tweet_count'],
                "original_url": url,
                "processing_time_seconds": round(processing_time, 2)
            },
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/summarize", response_class=HTMLResponse)
async def summarize_thread_form(request: Request, url: str = Form(...)):
    """
    Form endpoint for HTML form submissions
    """
    try:
        # Create a request object for the API call
        thread_request = ThreadRequest(url=url)
        
        # Call the API endpoint
        result = await summarize_thread_api(thread_request)
        
        # Return the results page
        return templates.TemplateResponse("index.html", {
            "request": request,
            "result": result.dict(),
            "url": url
        })
        
    except HTTPException as e:
        # Return error page
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": e.detail,
            "url": url
        })
    except Exception as e:
        logger.error(f"Form processing error: {str(e)}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"An unexpected error occurred: {str(e)}",
            "url": url
        })

@app.get("/api/providers")
async def get_providers_status():
    """
    Get the status of available LLM providers
    """
    if not thread_summarizer:
        return {"error": "Summarizer not initialized"}
    
    try:
        providers_info = []
        for provider in thread_summarizer.providers:
            try:
                temp_summarizer = ThreadSummarizer(provider)
                status = temp_summarizer.get_provider_status()
                providers_info.append({
                    "name": provider,
                    "available": True,
                    "status": status
                })
            except Exception as e:
                providers_info.append({
                    "name": provider,
                    "available": False,
                    "error": str(e)
                })
        
        return {
            "current_provider": thread_summarizer.providers[thread_summarizer.current_provider_index] if thread_summarizer.current_provider_index < len(thread_summarizer.providers) else None,
            "providers": providers_info
        }
    except Exception as e:
        return {"error": str(e)}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "error": "Page not found"
    })

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "error": "Internal server error occurred"
    })

if __name__ == "__main__":
    import uvicorn
    
    # Check for required environment variables
    required_vars = ['FIRECRAWL_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        print("\nRequired environment variables:")
        print("- FIRECRAWL_API_KEY: Your Firecrawl API key")
        print("- OPENAI_API_KEY: Your OpenAI API key (optional if using Mistral)")
        print("- MISTRAL_API_KEY: Your Mistral API key (optional if using OpenAI)")
        print("\nPlease set these in a .env file or as environment variables.")
        exit(1)
    
    # Run the application
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")  # Use localhost for local development
    
    print(f"\n[START] Twitter Thread Summarizer starting...")
    print(f"[URL] Server will be available at: http://{host}:{port}")
    print(f"[URL] Alternative URL: http://localhost:{port}")
    print(f"[HEALTH] Health check: http://{host}:{port}/health")
    print("\n[NOTE] Make sure you have set up your API keys in .env file!\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )