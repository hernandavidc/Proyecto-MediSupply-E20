#!/bin/bash
# Script de inicialización de base de datos para MediSupply Supplier Service
# Se ejecuta como init container en Kubernetes

set -e

echo "🚀 Iniciando script de inicialización de base de datos..."

# Esperar a que la base de datos esté disponible
echo "⏳ Esperando conexión a la base de datos..."
until python -c "
import os
import psycopg2
from urllib.parse import urlparse

try:
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print('DATABASE_URL no está definida')
        exit(1)
    
    # Parsear la URL de la base de datos
    parsed = urlparse(db_url)
    
    # Conectar a PostgreSQL
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path[1:],  # Remover el '/' inicial
        user=parsed.username,
        password=parsed.password
    )
    conn.close()
    print('✅ Conexión a base de datos exitosa')
except Exception as e:
    print(f'❌ Error conectando a la base de datos: {e}')
    exit(1)
"; do
    echo "Esperando conexión a la base de datos..."
    sleep 2
done

echo "✅ Base de datos disponible"

# Ejecutar el script de inicialización
echo "📊 Ejecutando inicialización de datos..."
cd /app
python scripts/init_database.py

echo "🎉 Inicialización completada exitosamente"
