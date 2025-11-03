#!/bin/bash
# start.sh - Script de inicio para el contenedor

set -e

echo "Starting User Service..."

# Esperar a que la base de datos esté disponible (con timeout de 60 segundos)
echo "Waiting for database (max 60 seconds)..."
MAX_ATTEMPTS=30
ATTEMPT=0
DB_READY=false

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if pg_isready -h medisupply-user-db -p 5432 -U user 2>/dev/null; then
        echo "Database is ready!"
        DB_READY=true
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "Database not ready, waiting... (attempt $ATTEMPT/$MAX_ATTEMPTS)"
    sleep 2
done

if [ "$DB_READY" = "false" ]; then
    echo "⚠️  Database not ready after 60 seconds, continuing anyway..."
    echo "ℹ️  Service will retry database connections automatically (pool_pre_ping=True)"
fi

# Ejecutar la aplicación (la aplicación es resiliente con pool_pre_ping=True)
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
