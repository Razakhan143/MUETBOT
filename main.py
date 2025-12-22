import os
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from app_main.api import retriever_qa
from data import data_processing, news_data_fetcher

# Load environment variables
load_dotenv()

# ============================================================
# Configuration
# ============================================================
OUTPUT_FILE = os.path.join("data", "website_documents", "muet_data.txt")
NEWS_FILE = os.path.join("data", "website_documents", "muet_circular_data.txt")
PK_TZ = timezone('Asia/Karachi')

# Global QA chain instance
qa_chain = None
scheduler = None


# ============================================================
# Scheduler Job Functions (must be regular functions for APScheduler)
# ============================================================
def run_data_extraction_job():
    """Wrapper to run async data extraction in scheduler"""
    try:
        asyncio.create_task(data_processing.run_data_extraction_whole(OUTPUT_FILE))
        print("✅ Data extraction job started")
    except Exception as e:
        print(f"❌ Data extraction job failed: {e}")


def run_news_fetch_job():
    """Wrapper to run async news fetching in scheduler"""
    try:
        asyncio.create_task(news_data_fetcher.main(NEWS_FILE))
        print("✅ News fetch job started")
    except Exception as e:
        print(f"❌ News fetch job failed: {e}")


# ============================================================
# FastAPI Lifespan (Startup/Shutdown)
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events"""
    global qa_chain, scheduler
    
    # Startup
    print("🚀 Starting MUET Chatbot API...")
    
    # Initialize QA Chain
    file_paths = [OUTPUT_FILE, NEWS_FILE]
    qa_chain = retriever_qa(file_paths, flag=True)
    
    if qa_chain is None:
        print("⚠️ Warning: QA Chain initialization failed")
    else:
        print("✅ QA Chain initialized successfully")
    
    # Initialize and start scheduler
    scheduler = AsyncIOScheduler(timezone=PK_TZ)
    
    # Schedule data extraction (one-time run on specific date)
    run_time = datetime(2026, 1, 1, 12, 0, 0)
    scheduler.add_job(
        run_data_extraction_job,
        'date',
        run_date=run_time,
        id='data_extraction_job'
    )
    
    # Schedule news fetching (daily at 12:00 PM)
    scheduler.add_job(
        run_news_fetch_job,
        'cron',
        hour=12,
        minute=0,
        id='news_fetch_job'
    )
    
    scheduler.start()
    print("📅 Scheduler started")
    
    yield  # Application runs here
    
    # Shutdown
    print("🛑 Shutting down...")
    if scheduler:
        scheduler.shutdown(wait=False)
        print("📅 Scheduler stopped")


# ============================================================
# FastAPI App
# ============================================================
app = FastAPI(
    title="MUET Chatbot API",
    description="RAG-based chatbot for MUET university information",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Request/Response Models
class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    status: str = "success"


# ============================================================
# API Routes
# ============================================================
@app.get("/")
def read_root():
    """Serve the frontend HTML page"""
    html_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "MUET Chatbot API is running", "status": "healthy"}


@app.get("/api")
def api_info():
    """API info endpoint"""
    return {"message": "MUET Chatbot API is running", "status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for the MUET chatbot
    """
    global qa_chain
    
    if qa_chain is None:
        raise HTTPException(
            status_code=503,
            detail="QA Chain not initialized. Please try again later."
        )
    
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        response = qa_chain.invoke(query)
        
        # Handle different response formats
        if isinstance(response, dict):
            answer = response.get("result", response.get("answer", str(response)))
        else:
            answer = str(response)
        
        return ChatResponse(answer=answer)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "qa_chain_ready": qa_chain is not None,
        "scheduler_running": scheduler is not None and scheduler.running if scheduler else False
    }


# ============================================================
# CLI Mode (for terminal-based chatbot)
# ============================================================
async def run_cli_chatbot():
    """Run the chatbot in CLI mode"""
    global qa_chain
    
    print("🔄 Initializing MUET Chatbot...")
    
    # Initialize QA Chain
    file_paths = [OUTPUT_FILE, NEWS_FILE]
    qa_chain = retriever_qa(file_paths, flag=True)
    
    if qa_chain is None:
        print("❌ Failed to initialize QA Chain. Exiting.")
        return
    
    print("\n🎓 MUET Chatbot Ready! (Type 'exit' to quit)")
    
    while True:
        try:
            query = input('\nUser: ')
        except EOFError:
            print("\nGoodbye!")
            break
            
        if query.lower() in ['exit', 'bye', 'escape', 'quit']:
            print("Goodbye!")
            break
        
        if not query.strip():
            continue
        
        try:
            response = qa_chain.invoke(query)
            
            if isinstance(response, dict):
                answer = response.get("result", response.get("answer", str(response)))
            else:
                answer = response
            
            print(f"\nAI Response: {answer}")
        except Exception as e:
            print(f"❌ Error during query: {str(e)}")


# ============================================================
# Main Entry Point
# ============================================================
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # Run in CLI mode
        try:
            asyncio.run(run_cli_chatbot())
        except KeyboardInterrupt:
            print("\n\nProcess stopped by user.")
    else:
        # Run as API server
        import uvicorn
        print("Starting MUET Chatbot API server...")
        print("Use --cli flag to run in terminal mode: python main.py --cli")
        uvicorn.run(app, host="0.0.0.0", port=8000)