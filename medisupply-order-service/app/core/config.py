import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL', 
        'sqlite:///./orders.db'
    )
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'replace_with_secure_secret')
    INTERNAL_SERVICE_KEY: str = os.getenv('INTERNAL_SERVICE_KEY', 'medisupply-internal-secret-key-2024')
    USER_SERVICE_URL: str = os.getenv('USER_SERVICE_URL', 'http://medisupply-user-service:8000')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    PROJECT_NAME: str = "medisupply-order-service"
    VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', '8000'))
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    class Config:
        env_file = '.env'

settings = Settings()
