"""
The Churn Poacher - FastAPI Application Entrypoint.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.db.session import init_db
from app.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Initializing The Churn Poacher backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT} | Demo Mode: {settings.DEMO_MODE}")
    logger.info(f"Database: {settings.DATABASE_URL.split('://')[0]}")
    
    # Initialize database tables on startup
    await init_db()
    logger.info("Database schema synchronized.")
    
    yield
    logger.info("Shutting down The Churn Poacher backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware for Next.js frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 routes
app.include_router(api_v1_router, prefix="/api")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend operational status."""
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "demo_mode": settings.DEMO_MODE,
        "database_backend": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql",
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to The Churn Poacher API",
        "docs": "/docs",
        "health": "/health",
        "api_v1": "/api/v1",
    }
