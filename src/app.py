"""
CoresAI Main Application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import logging
from pathlib import Path

from .discord_auth import router as auth_router
from .discord_integration import bot, run_bot
import asyncio
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CoresAI",
    description="CoresAI Trading Platform with Discord Integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path("frontend/build")
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

# Include routers
app.include_router(auth_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Start Discord bot in a separate thread"""
    def run_discord_bot():
        asyncio.set_event_loop(asyncio.new_event_loop())
        run_bot()
    
    thread = threading.Thread(target=run_discord_bot, daemon=True)
    thread.start()
    logger.info("Discord bot started")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8082,
        reload=True
    ) 