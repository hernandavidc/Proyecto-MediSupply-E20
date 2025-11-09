from fastapi import FastAPI, Request, HTTPException, status
import logging
import time
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_tables
from app.core.config import settings
from app.api.v1 import user_routes

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

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "user-service",
        "features": ["users", "audit"]
    }
