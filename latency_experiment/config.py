import os
from typing import Optional

class Settings:
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/latency_experiment"
    TEST_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/latency_experiment_test"
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1  # Different DB from security experiment
    
    # Cache Configuration
    CACHE_TTL_INVENTORY: int = 30      # 30 seconds for inventory
    CACHE_TTL_ORDER_STATUS: int = 10   # 10 seconds for order status
    CACHE_TTL_PRODUCT_INFO: int = 300  # 5 minutes for product info
    
    # Performance Configuration
    MAX_DB_CONNECTIONS: int = 20
    MIN_DB_CONNECTIONS: int = 5
    CONNECTION_TIMEOUT: int = 30
    
    # SLA Requirements
    INVENTORY_QUERY_SLA: float = 2.0   # seconds
    ORDER_STATUS_SLA: float = 1.0      # seconds
    PRODUCT_LOCATION_SLA: float = 1.0  # seconds
    
    # Testing Configuration
    LOAD_TEST_USERS: int = 50
    LOAD_TEST_DURATION: int = 60

settings = Settings()
