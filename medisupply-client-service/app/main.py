from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import client_routes
from app.core.database import create_tables
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create database tables
logger.info("Creating database tables...")
create_tables()
logger.info("Database tables created successfully")

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(client_routes.router)

# Health check endpoint
@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check if the service is running"
)
def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


@app.get(
    "/",
    tags=["Root"],
    summary="Root endpoint",
    description="Welcome message and API information"
)
def root():
    """
    Root endpoint
    """
    return {
        "message": "Welcome to MediSupply Client Service",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} starting up...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"{settings.PROJECT_NAME} shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

