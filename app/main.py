from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import leads, campaigns, emails, websites, followups, auth
from app.core.config import settings
from app.services.scheduler_service import SchedulerService
import logging
import sys

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler_service = SchedulerService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start scheduler
    logger.info("🚀 Starting application...")
    scheduler_service.start()
    logger.info("✅ Scheduler started")
    yield
    # Shutdown: Stop scheduler
    logger.info("🛑 Shutting down application...")
    scheduler_service.stop()
    logger.info("✅ Scheduler stopped")

app = FastAPI(
    title="Lead Scraping & Email Automation API",
    description="Backend API for Apollo lead scraping and automated email campaigns",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(emails.router, prefix="/api/emails", tags=["emails"])
app.include_router(websites.router, prefix="/api/websites", tags=["websites"])
app.include_router(followups.router, prefix="/api/followups", tags=["followups"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Lead Scraping & Email Automation API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

