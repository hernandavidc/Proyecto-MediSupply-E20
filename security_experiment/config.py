import os
from typing import Optional

class Settings:
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # JWT Configuration
    JWT_ALGORITHM: str = "RS256"
    JWT_EXPIRATION_MINUTES: int = 60
    
    # Security Configuration
    RATE_LIMIT_REQUESTS: int = 100  # requests per minute
    RATE_LIMIT_WINDOW: int = 60     # seconds
    
    # Alert Configuration
    SECURITY_ALERTS_ENABLED: bool = True
    
    def __init__(self):
        # Load private key
        with open('private_key.pem', 'rb') as f:
            self.JWT_PRIVATE_KEY = f.read()
        
        # Load public key
        with open('public_key.pem', 'rb') as f:
            self.JWT_PUBLIC_KEY = f.read()

settings = Settings()
