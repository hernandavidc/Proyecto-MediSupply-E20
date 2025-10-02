#!/bin/bash
# start.sh - Script de inicio para el contenedor

set -e

echo "Starting User Service..."

# Esperar a que la base de datos esté disponible
echo "Waiting for database..."
while ! pg_isready -h medisupply-user-db -p 5432 -U user; do
    echo "Database not ready, waiting..."
    sleep 2
done

echo "Database is ready!"

# Ejecutar la aplicación
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
