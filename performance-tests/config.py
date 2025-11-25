"""
Configuración para pruebas de performance
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Edge Proxy URL
# Opciones:
# - Producción: https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app
# - Local Docker: http://localhost:8080
# - Local Directo: http://localhost:8001 (user-service)
EDGE_PROXY_URL = os.getenv(
    'EDGE_PROXY_URL', 
    'https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app'  # Default a producción
)

# Test credentials
# Todos los usuarios tienen la contraseña: password123
# Opciones: admin@medisupply.com, jp@example.com (vendedor), conductor1@medisupply.com
TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL', 'admin@medisupply.com')
TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD', 'password123')

# Performance thresholds (SLAs)
LOCALIZATION_THRESHOLD = float(os.getenv('LOCALIZATION_THRESHOLD', '1.0'))  # ≤1s
ROUTE_OPTIMIZATION_THRESHOLD = float(os.getenv('ROUTE_OPTIMIZATION_THRESHOLD', '3.0'))  # ≤3s
ORDERS_PER_MINUTE_MIN = int(os.getenv('ORDERS_PER_MINUTE_MIN', '100'))  # 100 pedidos/min
ORDERS_PER_MINUTE_MAX = int(os.getenv('ORDERS_PER_MINUTE_MAX', '400'))  # 400 pedidos/min

# Locust configuration
LOCUST_USERS = int(os.getenv('LOCUST_USERS', '10'))  # Concurrent users
LOCUST_SPAWN_RATE = int(os.getenv('LOCUST_SPAWN_RATE', '2'))  # Users spawned per second
LOCUST_RUN_TIME = os.getenv('LOCUST_RUN_TIME', '1m')  # Run time

