"""
Task Control Center - FastAPI Server
A modern interface between frontend and backend for task and resource management.

Features:
- Task management with status tracking and progress monitoring
- Resource management (proxies, cards, emails, accounts)
- Real-time updates via WebSocket
- Beautiful, responsive web interface

Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# Import configuration
from app.core.config import settings

# Import routers
from app.routes import tasks_router, resources_router, monitoring_router

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="API interface for task and resource management",
    version=settings.APP_VERSION,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
)

# CORS middleware - using settings from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "app", "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include routers
app.include_router(tasks_router)
app.include_router(resources_router)
app.include_router(monitoring_router)


# Root endpoint - serve the frontend
@app.get("/")
async def root():
    """Serve the main frontend application."""
    return FileResponse(os.path.join(static_path, "index.html"))


# Health check endpoint
@app.get("/health")
async def health():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print(f"""
    ╔═══════════════════════════════════════════════╗
    ║         {settings.APP_NAME} v{settings.APP_VERSION}            ║
    ║    Modern Task & Resource Management API      ║
    ╠═══════════════════════════════════════════════╣
    ║  Environment: {settings.ENVIRONMENT:<30} ║
    ║  Documentation: http://{settings.HOST}:{settings.PORT}/docs    ║
    ║  Frontend:      http://{settings.HOST}:{settings.PORT}         ║
    ╚═══════════════════════════════════════════════╝
    """)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print(f"Shutting down {settings.APP_NAME}...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD or settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )
