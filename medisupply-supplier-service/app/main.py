from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import proveedor_routes, producto_routes, catalog_routes, plan_routes, vendedor_routes
from app.core.database import create_tables
from app.core.config import settings
import logging
import time

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Variable para rastrear si las tablas fueron creadas
_tables_created = False


def ensure_tables_exist():
    """
    Asegurar que las tablas existan. Reintenta automáticamente si falla.
    """
    global _tables_created
    
    if _tables_created:
        return True
    
    max_retries = 5
    retry_delay = 5  # segundos
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to create database tables (attempt {attempt + 1}/{max_retries})...")
            create_tables()
            logger.info("Database tables created successfully")
            _tables_created = True
            return True
        except Exception as e:
            logger.warning(f"Error creating database tables (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to create tables after {max_retries} attempts. Will retry on first request.")
    
    return False


# Intentar crear tablas al inicio (no bloquea si falla)
ensure_tables_exist()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Microservicio de proveedores - MediSupply",
    version=settings.VERSION,
    debug=settings.DEBUG,
    docs_url="/supplier-docs",
    redoc_url="/supplier-redoc",
    openapi_url="/supplier-openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(proveedor_routes.router)
app.include_router(producto_routes.router)
app.include_router(catalog_routes.router)
app.include_router(plan_routes.router)
app.include_router(vendedor_routes.router)

@app.get("/")
def root():
    return {
        "message": "MediSupply Supplier Service",
        "version": settings.VERSION,
        "docs": "/supplier-docs",
        "health": "/healthz"
    }

@app.get('/healthz')
def healthz():
    return {"status": "ok"}


@app.middleware("http")
async def ensure_tables_middleware(request: Request, call_next):
    """
    Middleware que asegura que las tablas existan antes de procesar requests.
    Solo verifica en requests que requieren base de datos.
    """
    # Si las tablas ya están creadas, continuar normalmente
    if _tables_created:
        return await call_next(request)
    
    # Solo verificar para rutas que requieren DB (api routes)
    if request.url.path.startswith("/api/"):
        # Intentar crear tablas si no existen
        if ensure_tables_exist():
            logger.info("Tables created automatically on first API request")
        else:
            # Si falla, continuar de todas formas (el error se verá en la respuesta)
            logger.warning("Could not create tables, request will likely fail")
    
    return await call_next(request)


@app.on_event("startup")
async def startup_event():
    """Evento de startup - reintenta crear tablas después de iniciar"""
    logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} starting up...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    # Reintentar crear tablas en background después de 10 segundos
    import asyncio
    
    async def retry_create_tables():
        await asyncio.sleep(10)  # Esperar 10s para que PostgreSQL esté listo
        logger.info("Retrying to create database tables after startup delay...")
        ensure_tables_exist()
    
    # Ejecutar en background sin bloquear (guardar referencia para evitar garbage collection)
    _startup_task = asyncio.create_task(retry_create_tables())
