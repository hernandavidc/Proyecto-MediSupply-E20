from fastapi import FastAPI, Request, HTTPException, status, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1 import (
    orden_routes,
    vehiculo_routes,
    bodega_routes,
    bodega_producto_routes,
    novedad_orden_routes,
    internal_routes
)
from app.core.dependencies import require_auth_security
from app.core.auth import require_auth
from app.core.database import create_tables
from app.core.config import settings
import os
import logging
import time

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

_tables_created = False


def ensure_tables_exist():
    global _tables_created
    
    if _tables_created:
        return True
    
    max_retries = 10
    retry_delay = 3
    
    for attempt in range(max_retries):
        try:
            from app.core.database import engine
            from sqlalchemy import text
            
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info(f"Attempting to create database tables (attempt {attempt + 1}/{max_retries})...")
            create_tables()
            
            ordenes_table_exists = False
            try:
                with engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = 'ordenes'
                        );
                    """))
                    ordenes_table_exists = bool(result.scalar())
            except Exception:
                try:
                    from sqlalchemy import inspect
                    inspector = inspect(engine)
                    ordenes_table_exists = inspector.has_table("ordenes")
                except Exception:
                    ordenes_table_exists = False

            if ordenes_table_exists:
                logger.info("Database tables created successfully")
                _tables_created = True
                return True
            else:
                raise Exception("Tables created but ordenes table not found")
                    
        except Exception as e:
            logger.warning(f"Error creating database tables (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to create tables after {max_retries} attempts. Will retry on first request.")
    
    return False


ensure_tables_exist()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Microservicio de ordenes y logística - MediSupply",
    version=settings.VERSION,
    debug=settings.DEBUG,
    docs_url="/order-docs",
    redoc_url="/order-redoc",
    openapi_url="/order-openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orden_routes.router, dependencies=[Security(require_auth_security)])
app.include_router(vehiculo_routes.router, dependencies=[Security(require_auth_security)])
app.include_router(bodega_routes.router, dependencies=[Security(require_auth_security)])
app.include_router(bodega_producto_routes.router, dependencies=[Security(require_auth_security)])
app.include_router(novedad_orden_routes.router, dependencies=[Security(require_auth_security)])
# Rutas internas sin auth pero con header especial (verificado en middleware)
app.include_router(internal_routes.router)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path    
    exempt_prefixes = [
        '/',
        '/healthz',
        '/order-docs',
        '/order-redoc',
        '/order-openapi.json',
        '/order-openapi',
    ]
    
    # Endpoint interno SOLO para comunicación entre servicios
    if path.startswith('/internal/v1/ordenes') and request.method == 'GET':
        internal_key = request.headers.get('X-Internal-Service-Key')
        
        # Verificar header de autenticación interna
        if internal_key and internal_key == settings.INTERNAL_SERVICE_KEY:
            request.state.user = {"id": 0, "email": "internal-service", "name": "Internal Service", "is_active": True}
            return await call_next(request)
        else:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Forbidden: Invalid internal service key"}
            )
    
    if any(path == p or path.startswith(p + '/') for p in exempt_prefixes):
        return await call_next(request)

    if os.getenv('AUTH_DISABLED', 'false').lower() == 'true':
        request.state.user = {"id": 0, "email": "test@local", "name": "test-user", "is_active": True}
    else:
        try:
            user_json = require_auth(request)
            request.state.user = user_json
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return await call_next(request)


@app.get("/")
def root():
    return {
        "message": "MediSupply Order Service",
        "version": settings.VERSION,
        "docs": "/order-docs",
        "health": "/healthz"
    }


@app.get('/healthz')
def healthz():
    from app.core.database import engine
    from sqlalchemy import text
    
    try:
        with engine.connect() as conn:
            ordenes_table_exists = False
            try:
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'ordenes'
                    );
                """))
                ordenes_table_exists = bool(result.scalar())
            except Exception:
                try:
                    from sqlalchemy import inspect
                    inspector = inspect(engine)
                    ordenes_table_exists = inspector.has_table("ordenes")
                except Exception:
                    ordenes_table_exists = False

            if not ordenes_table_exists:
                ensure_tables_exist()
                try:
                    result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = 'ordenes'
                        );
                    """))
                    ordenes_table_exists = bool(result.scalar())
                except Exception:
                    try:
                        from sqlalchemy import inspect
                        inspector = inspect(engine)
                        ordenes_table_exists = inspector.has_table("ordenes")
                    except Exception:
                        ordenes_table_exists = False

            if not ordenes_table_exists:
                logger.warning("Health check: ordenes table does not exist yet")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "status": "degraded",
                        "service": "order-service",
                        "database": "connected",
                        "tables": "not_ready",
                        "message": "Database connected but tables not created yet"
                    }
                )
        
        return {
            "status": "healthy",
            "service": "order-service",
            "database": "connected",
            "tables": "ready"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "service": "order-service",
                "database": "disconnected",
                "error": str(e)
            }
        )


@app.middleware("http")
async def ensure_tables_middleware(request: Request, call_next):
    if _tables_created:
        return await call_next(request)
    
    if request.url.path.startswith("/api/"):
        if ensure_tables_exist():
            logger.info("Tables created automatically on first API request")
        else:
            logger.warning("Could not create tables, request will likely fail")
    
    return await call_next(request)


@app.on_event("startup")
async def startup_event():
    logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} starting up...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    import asyncio
    
    async def retry_create_tables():
        await asyncio.sleep(10)
        logger.info("Retrying to create database tables after startup delay...")
        ensure_tables_exist()
    
    _startup_task = asyncio.create_task(retry_create_tables())
