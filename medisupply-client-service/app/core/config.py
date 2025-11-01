import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Project metadata
    PROJECT_NAME: str = "MediSupply Client Service"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Client management and registration service for institutional clients"
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Database configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://client_user:client_password@medisupply-client-db:5432/clients_db"
    )
    
    # Security - IMPORTANTE: Debe ser la misma SECRET_KEY que User Service
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    )
    ALGORITHM: str = "HS256"  # Debe ser el mismo que User Service
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # External services
    NIT_VALIDATION_SERVICE_URL: Optional[str] = None
    
    # User Service URL (para Swagger UI y referencias)
    USER_SERVICE_URL: str = os.getenv(
        "USER_SERVICE_URL",
        "http://medisupply-user-service:8000"  # Para docker-compose local
    )
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

