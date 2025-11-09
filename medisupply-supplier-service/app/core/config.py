import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DATABASE_URL: Por defecto usa SQLite SOLO para testing local
    # En producción (Kubernetes) se debe pasar DATABASE_URL como variable de entorno
    # con conexión a PostgreSQL (ver supplier-service-secret.yaml)
    # Formato esperado: postgresql://user:password@host:port/database
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL', 
        'sqlite:///./supplier.db'  # Solo para desarrollo/testing local
    )
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'replace_with_secure_secret')
    # URL base del servicio de usuarios (usado para validar tokens remotamente)
    USER_SERVICE_URL: str = os.getenv('USER_SERVICE_URL', 'http://medisupply-user-service:8000')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    PROJECT_NAME: str = "medisupply-supplier-service"
    VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', '8000'))

    class Config:
        env_file = '.env'

settings = Settings()
