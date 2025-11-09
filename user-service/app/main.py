from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_tables
from app.core.config import settings
from app.api.v1 import user_routes

# Crear las tablas en la base de datos
create_tables()

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
