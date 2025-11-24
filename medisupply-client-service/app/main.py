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

# Create database tables (with error handling)
try:
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")
    logger.warning("Service will continue but database operations may fail")

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    debug=settings.DEBUG,
    docs_url="/client-docs",
    redoc_url="/client-redoc",
    openapi_url="/client-openapi.json"
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
    tags=["Salud"],
    summary="Verificación de salud",
    description="Verificar si el servicio está en ejecución"
)
def health_check():
    """
    Endpoint de verificación de salud
    """
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

# Client health check endpoint (para el Gateway)
@app.get(
    "/client-health",
    tags=["Salud"],
    summary="Verificación de salud (Gateway)",
    description="Verificar si el servicio está en ejecución (ruta del Gateway)"
)
def client_health_check():
    """
    Endpoint de verificación de salud para el Gateway
    """
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


@app.get(
    "/",
    tags=["Raíz"],
    summary="Endpoint raíz",
    description="Mensaje de bienvenida e información de la API"
)
def root():
    """
    Endpoint raíz
    """
    return {
        "message": "Bienvenido al Servicio de Clientes MediSupply",
        "version": settings.VERSION,
        "docs": "/client-docs",
        "health": "/health"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} starting up...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    # Ejecutar seeds en background después de 5 segundos
    import asyncio
    
    async def load_seed_data():
        await asyncio.sleep(5)  # Esperar para asegurar que la DB esté lista
        try:
            from app.core.seed_data import seed_data
            logger.info("Executing seed data...")
            seed_data()
            logger.info("✅ Seed data loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load seed data: {e}")
    
    # Ejecutar en background
    _seed_task = asyncio.create_task(load_seed_data())


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

