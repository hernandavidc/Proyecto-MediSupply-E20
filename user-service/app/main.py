from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_tables
from app.core.config import settings
from app.api.v1 import user_routes
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
            
            # Verificar que las tablas se crearon correctamente
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'users'
                    );
                """))
                if result.scalar():
                    logger.info("Database tables created successfully")
                    _tables_created = True
                    return True
                else:
                    raise Exception("Tables created but users table not found")
                    
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
    description="Microservicio de usuarios para el sistema MediSupply",
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
from app.api.v1 import user_routes

app.include_router(user_routes.router)

@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "message": "User Service - MediSupply API",
        "version": settings.VERSION,
        "endpoints": {
            "users": "/api/v1/users",
            "providers": "/api/v1/providers",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/api/v1/roles")
def get_roles():
    """
    📋 Listar todos los roles disponibles
    
    Endpoint público para que otros servicios puedan consultar 
    los roles disponibles y sus IDs.
    
    Este endpoint es utilizado por client-service para obtener 
    dinámicamente el ID del rol "Cliente".
    """
    from app.core.database import SessionLocal
    from app.models.role import Role
    
    db = SessionLocal()
    try:
        roles = db.query(Role).order_by(Role.id).all()
        return [{"id": role.id, "name": role.name} for role in roles]
    finally:
        db.close()

@app.get("/health")
def health_check():
    """Health check endpoint - verifica conexión a BD y tablas"""
    from app.core.database import engine
    from sqlalchemy import text
    
    try:
        # Verificar conexión a la base de datos
        with engine.connect() as conn:
            # Verificar que las tablas existan
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """))
            users_table_exists = result.scalar()
            
            if not users_table_exists:
                # Intentar crear tablas si no existen
                ensure_tables_exist()
                # Verificar nuevamente
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'users'
                    );
                """))
                users_table_exists = result.scalar()
            
            if not users_table_exists:
                logger.warning("Health check: users table does not exist yet")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "status": "degraded",
                        "service": "user-provider-service",
                        "database": "connected",
                        "tables": "not_ready",
                        "message": "Database connected but tables not created yet"
                    }
                )
        
        return {
            "status": "healthy", 
            "service": "user-provider-service",
            "database": "connected",
            "tables": "ready",
            "features": ["users", "providers", "audit"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "service": "user-provider-service",
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
