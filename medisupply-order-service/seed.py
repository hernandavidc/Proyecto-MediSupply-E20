#!/usr/bin/env python3
"""
Script para cargar datos iniciales (seed) en el order-service.

Uso:
    python seed.py
    
O desde Docker:
    docker exec medisupply-order-service python seed.py
"""

import sys
import os

# Agregar el directorio app al path para poder importar
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.seed_data import seed_data

if __name__ == "__main__":
    print("=" * 60)
    print("   SEED DATA - Order Service")
    print("=" * 60)
    print()
    
    seed_data()
    
    print()
    print("=" * 60)
    print("   ✅ Proceso completado")
    print("=" * 60)
