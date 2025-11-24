from fastapi import FastAPI, Request, HTTPException, status, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1 import proveedor_routes, producto_routes, catalog_routes, plan_routes, vendedor_routes, report_routes, visita_routes
from app.api.v1 import user_lookup_routes
from app.core.dependencies import get_current_user, require_auth_security
from app.core.auth import require_auth
from app.core.database import create_tables
import os
from app.core.seed_data import seed_data
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
    
    max_retries = 10  # Aumentar reintentos
    retry_delay = 3  # segundos (reducir delay para ser más rápido)
    
    for attempt in range(max_retries):
        try:
            # Primero verificar conexión a la BD
            from app.core.database import engine
            from sqlalchemy import text
            
            with engine.connect() as conn:
                # Verificar que la base de datos existe y podemos conectarnos
                conn.execute(text("SELECT 1"))
            
            logger.info(f"Attempting to create database tables (attempt {attempt + 1}/{max_retries})...")
            create_tables()
            
            # Verificar que las tablas se crearon correctamente.
            # Intentar la comprobación específica de Postgres; si falla (p.ej. SQLite),
            # hacer un fallback portable usando SQLAlchemy inspector.
            proveedores_table_exists = False
            try:
                with engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = 'proveedores'
                        );
                    """))
                    proveedores_table_exists = bool(result.scalar())
            except Exception:
                # Fallback portable
                try:
                    from sqlalchemy import inspect
                    inspector = inspect(engine)
                    proveedores_table_exists = inspector.has_table("proveedores")
                except Exception:
                    proveedores_table_exists = False

            if proveedores_table_exists:
                logger.info("Database tables created successfully")
                _tables_created = True
                return True
            else:
                raise Exception("Tables created but proveedores table not found")
                    
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

app.include_router(proveedor_routes.router, dependencies=[Security(require_auth_security)])
app.include_router(producto_routes.router, dependencies=[Security(require_auth_security)])
app.include_router(catalog_routes.router, dependencies=[Security(require_auth_security)])
app.include_router(plan_routes.router, dependencies=[Security(require_auth_security)])
app.include_router(vendedor_routes.router, dependencies=[Security(require_auth_security)])
app.include_router(report_routes.router, dependencies=[Security(require_auth_security)])
app.include_router(visita_routes.router, dependencies=[Security(require_auth_security)])
app.include_router(user_lookup_routes.router, dependencies=[Security(require_auth_security)])


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Middleware global que valida el token en Authorization: Bearer <token>

    Exime rutas públicas como health y la documentación.
    Si el token es válido, añade `request.state.user` con el JSON del usuario.
    """
    path = request.url.path    
    # Rutas públicas que no requieren autenticación
    exempt_prefixes = [
        '/',
        '/healthz',
        '/supplier-docs',
        '/supplier-redoc',
        '/supplier-openapi.json',
        '/supplier-openapi',
    ]
    if any(path == p or path.startswith(p + '/') for p in exempt_prefixes):
        return await call_next(request)

    # Allow tests / CI to disable auth via env var (AUTH_DISABLED=true)
    if os.getenv('AUTH_DISABLED', 'false').lower() == 'true':
        # attach a dummy test user
        request.state.user = {"id": 0, "email": "test@local", "name": "test-user", "is_active": True}
    else:
        try:
            user_json = require_auth(request)
            # attach user info to the request so endpoints can use it if needed
            request.state.user = user_json
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return await call_next(request)

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
    """Health check endpoint - verifica conexión a BD y tablas"""
    from app.core.database import engine
    from sqlalchemy import text
    
    try:
        # Verificar conexión a la base de datos
        with engine.connect() as conn:
            # Intentar la comprobación específica de Postgres; si falla, usar inspector
            proveedores_table_exists = False
            try:
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'proveedores'
                    );
                """))
                proveedores_table_exists = bool(result.scalar())
            except Exception:
                # Fallback: comprobar con SQLAlchemy inspector
                try:
                    from sqlalchemy import inspect
                    inspector = inspect(engine)
                    proveedores_table_exists = inspector.has_table("proveedores")
                except Exception:
                    proveedores_table_exists = False

            if not proveedores_table_exists:
                # Intentar crear tablas si no existen
                ensure_tables_exist()
                # Verificar nuevamente con fallback
                try:
                    result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = 'proveedores'
                        );
                    """))
                    proveedores_table_exists = bool(result.scalar())
                except Exception:
                    try:
                        from sqlalchemy import inspect
                        inspector = inspect(engine)
                        proveedores_table_exists = inspector.has_table("proveedores")
                    except Exception:
                        proveedores_table_exists = False

            if not proveedores_table_exists:
                logger.warning("Health check: proveedores table does not exist yet")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "status": "degraded",
                        "service": "supplier-service",
                        "database": "connected",
                        "tables": "not_ready",
                        "message": "Database connected but tables not created yet"
                    }
                )
        
        return {
            "status": "healthy",
            "service": "supplier-service",
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
                "service": "supplier-service",
                "database": "disconnected",
                "error": str(e)
            }
        )


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
    """Evento de startup - reintenta crear tablas y ejecutar seeds después de iniciar"""
    logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} starting up...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    # Reintentar crear tablas y ejecutar seeds en background después de 10 segundos
    import asyncio
    
    async def retry_create_tables_and_seed():
        await asyncio.sleep(10)  # Esperar 10s para que PostgreSQL esté listo
        logger.info("Retrying to create database tables after startup delay...")
        if ensure_tables_exist():
            # Si las tablas se crearon exitosamente, ejecutar seeds
            try:
                from app.core.seed_data import seed_data
                logger.info("Executing seed data...")
                seed_data()
                logger.info("✅ Seed data loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load seed data: {e}")
    
    # Ejecutar en background sin bloquear (guardar referencia para evitar garbage collection)
    _startup_task = asyncio.create_task(retry_create_tables_and_seed())
